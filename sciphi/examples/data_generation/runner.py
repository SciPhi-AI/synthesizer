"""Run the zero-shot replication."""
import argparse
import hashlib
import os
import secrets

from sciphi.core.utils import (
    get_configured_logger,
    get_data_config_dir,
    get_root_dir,
)
from sciphi.examples.helpers import (
    build_llm_config,
    parse_arguments,
    prep_for_file_path,
)
from sciphi.interface import InterfaceManager, ProviderName
from sciphi.llm import LLMConfigManager
from sciphi.makers import DataMaker
from sciphi.prompt import Prompt, PromptStructure
from sciphi.writers import JsonlDataWriter

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
    logger = get_configured_logger("sciphi", log_level=args.log_level)

    if args.num_samples % args.batch_size != 0:
        raise ValueError(
            f"Number of samples ({args.num_samples}) must be divisible by batch size ({args.batch_size})."
        )
    if args.num_samples < args.batch_size:
        raise ValueError(
            "Number of samples must be greater than batch size0. Please set --num_samples."
        )

    model_name = args.model_name
    provider_name = ProviderName(args.provider_name)

    logger.info(
        f"Loading ModelName={model_name} from ProviderName={provider_name.value}."
    )

    # Build an LLM and provider interface
    llm_config = LLMConfigManager.get_config_for_provider(
        provider_name
    ).create(**build_llm_config(args))
    llm_provider = InterfaceManager.get_provider(
        provider_name,
        model_name,
        llm_config,
    )

    # Initialize the data maker
    data_maker = DataMaker()
    data_maker.load_config_from_yaml(
        args.config_path
        or os.path.join(get_data_config_dir(), f"{args.example_config}.yaml")
    )

    if args.prompt_override != "":
        logger.debug(f"Overriding prompt with: {args.prompt_override}")
        prompt_inputs = args.prompt_override.split(",")
        data_maker.prompt = Prompt(
            text=prompt_inputs[0],
            expected_inputs=set(prompt_inputs[1:]),
            structure=PromptStructure.SINGLE,
        )

    # Generate & write out the results
    output_path = get_output_path(args)
    logger.debug(f"Writing results to: {output_path}.")
    writer = JsonlDataWriter(output_path)

    batch = []
    for entry in data_maker.generator(args.batch_size, args.num_samples):
        batch.append(entry)

        if len(batch) == args.batch_size:
            completions = llm_provider.get_batch_completion(
                [entry["formatted_prompt"] for entry in batch]
            )

            for it, completion in enumerate(completions):
                formatted_prompt = batch[it]["formatted_prompt"]
                logger.debug("-" * 100)
                logger.debug(f"Formatted Prompt:\n{formatted_prompt}")
                logger.debug(f"\nCompletion:\n{completion}")
                logger.debug("-" * 100)

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
