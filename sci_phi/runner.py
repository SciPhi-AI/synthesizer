"""Run the zero-shot replication."""
import os
import yaml

from sci_phi.core.utils import (
    get_configured_logger,
    get_config_dir,
    get_root_dir,
    parse_arguments,
    prep_for_file_path,
)
from sci_phi.interface import InterfaceManager, ProviderName
from sci_phi.llm import LLMConfigManager
from sci_phi.prompt import PromptManager, Prompt
from sci_phi.synthesizers import synthesize

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
                "EXTRA": args.extra,
            }.items()
        }
    )

    return os.path.join(output_dir, output_file_name)


if __name__ == "__main__":
    """Run the zero-shot replication."""
    # Setup
    logger = get_configured_logger("sci_phi", log_level="INFO")
    args = parse_arguments()

    model_name = args.model_name
    provider_name = ProviderName(args.provider_name)

    logger.info(
        f"Loading ModelName={model_name} from ProviderName={provider_name.value}."
    )

    # TODO - Intelligently modify LLMCofig to allow extra fields, like `top_k`
    # which exist for some but not for other inherited configs
    # Further, figure out how to intelligently pass all possible values from the CLI
    llm_config = LLMConfigManager.get_config_for_provider(provider_name)(
        provider_name=provider_name,
        model_name=model_name,
        temperature=args.temperature,
        # top_k=args.top_k,
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

    with open(
        os.path.join(get_config_dir(), "python_textbook.yaml"), "r"
    ) as file:
        input_generators = yaml.safe_load(file)

    synthesized_data = synthesize(prompt, input_generators, 1_024)
    for i in range(10):
        print(f"Synthesized data {i} = {synthesized_data[i]}")

    # Get the output path
    vargs = vars(args)
    vargs["version"] = llm_provider.model.config.version
    out_path = get_output_path(args)

    # Load existing results
    # results = load_existing_jsonl(out_path)
    # exising_task_ids = {
    # result["task_id"] for result in results if "task_id" in result
    # }

    # # Run the experiment
    # for task_id, problem in dataset.generator:
    #     if task_id in exising_task_ids:
    #         print(
    #             f"Continuing over existing task_id: {task_id} as it already exists."
    #         )
    #         continue

    #     prompt = llm_provider.model.get_formatted_prompt(problem, dataset)

    #     print(f"\n{'-'*200}\nTaskId:\n{task_id}\nPrompt:\n{prompt}\n")
    #     try:
    #         raw_completion = llm_provider.get_completion(prompt)
    #         if args.pset in ["human-eval", "leetcode", "leetcode-msft-sparks"]:
    #             # or other codegen
    #             completion = extract_code(raw_completion)
    #         else:
    #             completion = raw_completion

    #         print(f"Extracted Completion:\n{completion}\n")

    #         result = {
    #             **problem,
    #             "task_id": task_id,
    #             "completion": completion,
    #             "raw_completion": raw_completion,
    #             "actual_prompt": prompt,
    #         }
    #         results.append(result)

    #     except (
    #         openai.error.OpenAIError,
    #         Exception,
    #     ) as e:  # Catch any OpenAI specific errors and general exceptions
    #         print(f"Error encountered for task_id {task_id}: {e}")
    #         result = {
    #             **problem,
    #             "task_id": task_id,
    #             "completion": "Error encountered",
    #             "raw_completion": "Error encountered",
    #             "actual_prompt": prompt,
    #         }

    #     write_jsonl(out_path, results)
