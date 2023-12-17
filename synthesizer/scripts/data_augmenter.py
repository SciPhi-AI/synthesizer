"""A module which facilitates data augmentation.""" ""
import json
import logging
import os
from typing import Optional

import dotenv
import fire
import yaml
from datasets import Dataset, load_dataset
from tqdm import tqdm

from synthesizer.core import (
    JsonlDataWriter,
    LLMProviderName,
    Prompt,
    RAGProviderName,
)
from synthesizer.core.utils import get_config_dir
from synthesizer.interface import LLMInterfaceManager, RAGInterfaceManager
from synthesizer.llm import GenerationConfig

# Load environment variables
dotenv.load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_output_path(output_dir: str, output_name: str) -> str:
    """Returns the complete path where the output will be saved."""
    return (
        os.path.join(output_dir, output_name)
        if os.path.isabs(output_dir)
        else os.path.join(os.getcwd(), output_dir, output_name)
    )


def ensure_directory_exists(filepath: str):
    """Ensures the directory of the given filepath exists."""
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)


SHUFFLE_SEED = 42


def main(
    # Run Settings
    output_dir="augmented_output",
    output_name=None,
    shuffle: bool = True,
    n_samples: int = 100,
    # LLM Settings
    llm_provider_name="sciphi",
    llm_model_name="SciPhi/SciPhi-Mistral-7B-32k",
    llm_max_tokens_to_sample=128,
    llm_temperature=0.1,
    llm_top_k=100,
    llm_api_base: Optional[str] = "https://api.sciphi.ai/v1",
    llm_skip_special_tokens: bool = False,
    # RAG Settings
    rag_enabled=True,
    rag_provider_name="agent-search",
    rag_api_base="https://api.sciphi.ai",
    # Dataset Settings
    dataset_name: Optional[str] = None,
    dataset_split: str = "train",
    # Prompt Settings
    config_name: Optional[str] = "answer_question",
    config_path: Optional[str] = None,
    ## Additional user inputs (like user_supplied_suffix)
    ## can be passed in through Fire as kwargs, e.g.
    ## --user_supplied_inputs "{'your_input': 'Your Input Value'}"
    user_supplied_inputs: Optional[dict] = None,
    **kwargs,
):
    """Run the data augmenter."""

    # Validate configurations
    if config_name and config_path:
        raise ValueError(
            "Must provide either a config name or a config path, but not both."
        )

    # Initialize configuration and output path
    config_path_from_name_or_default = config_path or os.path.join(
        get_config_dir(), "prompts", f"{config_name}.yaml"
    )
    with open(config_path_from_name_or_default, "r") as yaml_file:
        config = yaml.safe_load(yaml_file)

    # Set default dataset name if not provided
    dataset_name = dataset_name or config["default_dataset_name"]

    # Set the default user supplied inputs
    user_supplied_inputs = (
        user_supplied_inputs or config["default_user_inputs_map"]
    )

    # Set up output settings

    ## Get the configuration name and the output file name
    config_name = config_path_from_name_or_default.split(os.path.sep)[
        -1
    ].replace(".yaml", "")
    output_name = (
        output_name
        or f"config_name_eq_{config_name}__dataset_name_eq_{dataset_name.replace('/','_')}.jsonl"
    )
    logger.info(
        f"Augmenting dataset {dataset_name} with prompt {config_name}."
    )

    logger.info(f"Saving the output to {output_name}.")
    output_path = get_output_path(output_dir, output_name)

    ## Ensure output directory exists
    ensure_directory_exists(output_path)
    writer = JsonlDataWriter(output_path)

    prompt = Prompt(config=config)
    rag_interface = (
        RAGInterfaceManager.get_interface_from_args(
            RAGProviderName(rag_provider_name),
            api_base=rag_api_base or llm_api_base,
        )
        if rag_enabled
        else None
    )

    llm_interface = LLMInterfaceManager.get_interface_from_args(
        LLMProviderName(llm_provider_name),
        api_base=llm_api_base,
        # Currently only consumed by SciPhi
        rag_interface=rag_interface,
        # Consumed by single-load providers
        model_name=llm_model_name,
    )

    llm_generation_config = GenerationConfig(
        temperature=llm_temperature,
        top_k=llm_top_k,
        max_tokens_to_sample=llm_max_tokens_to_sample,
        model_name=llm_model_name,
    )
    # Prepare the samples
    dataset: Dataset = load_dataset(dataset_name)[dataset_split]

    if shuffle:
        dataset = dataset.shuffle(seed=SHUFFLE_SEED)
    n_samples = min(n_samples, len(dataset))
    samples = dataset.select(range(n_samples))

    logger.info(f"Now running over {n_samples} samples.")
    for entry in tqdm(samples):
        user_supplied_inputs["rag_context"] = rag_interface.get_rag_context(
            entry["question"]
        )
        formatted_prompt = prompt.format(
            dataset_entry=entry, **user_supplied_inputs
        )
        completion = llm_interface.get_completion(
            formatted_prompt, llm_generation_config
        )
        if config["output_format"] == "jsonl":
            try:
                data = {
                    "formatted_prompt": formatted_prompt,
                    "completion": completion,
                }
                writer.write([data])
            except json.decoder.JSONDecodeError:
                logger.error(
                    f"Failed to decode JSON response from LLM: {completion}"
                )
        else:
            writer.write(
                [{"prompt": formatted_prompt, "completion": completion}]
            )


if __name__ == "__main__":
    fire.Fire(main)
