"""Run the zero-shot replication."""
import argparse
import hashlib
import os
import random
import secrets

from sci_phi.core.utils import (
    get_configured_logger,
    get_data_config_dir,
    get_root_dir,
)
from sci_phi.examples.helpers import (
    build_llm_config,
    parse_arguments,
    prep_for_file_path,
)
from sci_phi.interface import InterfaceManager, ProviderName
from sci_phi.llm import LLMConfigManager
from sci_phi.prompt import Prompt, PromptManager
from sci_phi.synthesizers import DataSynthesizer
from sci_phi.writers import JsonlDataWriter

random.seed(42)

OUTPUT_FILE_NAME = "{RUN_NAME}__provider_eq_{PROVIDER}__model_eq_{MODEL}__version_eq_{VERSION}{EXTRA}.jsonl"


def get_output_path(args: argparse.Namespace) -> str:
    """Get the output path for the given arguments."""

    def generate_random_hash() -> str:
        """Generate a random hash."""
        # Generate a random token in byte format and then convert to SHA256 hash
        random_token = secrets.token_bytes(32)  # 32 bytes = 256 bits
        return hashlib.sha256(random_token).hexdigest()

    output_dir = os.path.join(
        get_root_dir(),
        prep_for_file_path(args.output_dir),
        prep_for_file_path(args.provider_name),
        prep_for_file_path(args.model_name),
    )

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file_name = OUTPUT_FILE_NAME.format(
        **{
            k: prep_for_file_path(v)
            for k, v in {
                "RUN_NAME": args.run_name,
                "PROVIDER": str(args.provider_name),
                "MODEL": args.model_name,
                "VERSION": args.version,
                "EXTRA": args.extra_output_file_text
                or f"_{generate_random_hash()}",
            }.items()
        }
    )

    return os.path.join(output_dir, output_file_name)


if __name__ == "__main__":
    """Run the synthesis."""
    # Setup
    args = parse_arguments()
    logger = get_configured_logger("sci_phi", log_level=args.log_level)

    model_name = args.model_name
    provider_name = ProviderName(args.provider_name)

    logger.info(
        f"Loading ModelName={model_name} from ProviderName={provider_name.value}."
    )

    # Build an LLM and provider interface
    config_args = build_llm_config(args)
    llm_config = LLMConfigManager.get_config_for_provider(
        provider_name
    ).create(**config_args)
    llm_provider = InterfaceManager.get_provider(
        provider_name,
        model_name,
        llm_config,
    )

    # Build the input prompt(s)
    if args.prompt_override == "":
        prompt = PromptManager.get_prompt(args.prompt_type)
    elif args.prompt_type == "override":
        prompt_inputs = args.prompt_override.split(",")
        prompt = [
            Prompt(
                text=prompt_inputs[0],
                expected_inputs=set(prompt_inputs[1:]),
            )
        ]
    else:
        raise ValueError(
            "Set prompt_type to override if overriding the base prompt."
        )

    # Build the synthesizer
    synthesizer = DataSynthesizer(prompt)
    synthesizer.load_config_from_yaml(
        args.config_path
        or os.path.join(get_data_config_dir(), f"{args.example_config}.yaml")
    )

    output_path = get_output_path(args)
    logger.debug(f"Writing results to: {output_path}.")
    writer = JsonlDataWriter(output_path)

    # Generate the synthesized data
    batch = []
    for entry in synthesizer.synthesis_generator(args.num_samples):
        batch.append(entry)

        if len(batch) == args.batch_size:
            completions = [
                llm_provider.get_completion(entry["formatted_prompt"])
                for entry in batch
            ]

            for it, completion in enumerate(completions):
                formatted_prompt = batch[it]["formatted_prompt"]
                logger.debug(f"Formatted Prompt:\n{formatted_prompt}")

                logger.debug(f"Completion:\n{completion}")

                # Write the results using DataWriter
                writer.write(
                    [
                        {
                            "formatted_prompt": formatted_prompt,
                            "completion": completion,
                        }
                    ]
                )

            batch = []

            break
