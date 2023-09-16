"""Run the zero-shot replication."""
import os

from sci_phi.core.utils import (
    get_configured_logger,
    get_data_config_dir,
    get_root_dir,
    parse_arguments,
    prep_for_file_path,
)
from sci_phi.interface import InterfaceManager, ProviderName
from sci_phi.llm import LLMConfigManager
from sci_phi.prompt import PromptManager, Prompt
from sci_phi.synthesizers import DataSynthesizer

OUTPUT_FILE_NAME = "{RUN_NAME}__provider_eq_{PROVIDER}__model_eq_{MODEL}__version_eq_{VERSION}{EXTRA}.jsonl"


def get_output_path(args: dict) -> str:
    """Get the output path for the given arguments."""

    output_dir = os.path.join(
        *(
            prep_for_file_path(ele)
            for ele in [
                get_root_dir(),
                args.output_dir,
                args.provider_name,
                args.model_name,
            ]
        )
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
                "EXTRA": args.extra_output_file_text,
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

    llm_config = LLMConfigManager.get_config_for_provider(
        provider_name
    ).create(
        provider_name=provider_name,
        model_name=model_name,
        temperature=args.temperature,
        top_k=args.top_k,
        top_p=args.top_p,
    )

    # Build an LLM provider instance
    llm_provider = InterfaceManager.get_provider(
        provider_name,
        model_name,
        llm_config,
    )

    # Build the input prompt
    if args.prompt_override == "":
        prompt = PromptManager.get_prompt(args.prompt_type)
    elif args.prompt_type == "override":
        prompt_inputs = args.prompt_override.split(",")
        prompt = Prompt(
            text=prompt_inputs[0],
            expected_inputs=set(prompt_inputs[1:]),
        )
    else:
        raise ValueError(
            "Set prompt_type to override if overriding the base prompt."
        )

    # Generate the synthesized data
    synthesizer = DataSynthesizer(prompt)
    if not args.config_path:
        synthesizer.load_config_from_yaml(
            os.path.join(get_data_config_dir(), f"{args.example_config}.yaml")
        )
    else:
        synthesizer.load_config_from_yaml(args.config_path)

    for entry in synthesizer.synthesis_generator(args.num_samples):
        # TODO - Intelligently modify LLMCofig to allow extra fields, like `top_k`
        # which exist for some but not for other inherited configs
        # Further, figure out how to intelligently pass all possible values from the CLI

        logger.debug(f"Formatted Prompt:\n{entry['formatted_prompt']}")
        completion = llm_provider.get_completion(entry["formatted_prompt"])
        entry["completion"] = completion
        logger.debug(f"Completion:\n{completion}")
        break
