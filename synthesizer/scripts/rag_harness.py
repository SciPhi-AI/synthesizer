import logging
from typing import Optional

import dotenv
import fire
from tqdm import tqdm

from synthesizer.core import LLMProviderName, RAGProviderName
from synthesizer.eval.rag import ScienceMultipleChoiceEvaluator
from synthesizer.interface import LLMInterfaceManager, RAGInterfaceManager
from synthesizer.llm import GenerationConfig

# Load environment variables
dotenv.load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(
    # LLM Settings
    llm_provider_name="sciphi",
    llm_model_name="SciPhi/Sensei-7B-V1",
    llm_max_tokens_to_sample=32,
    llm_temperature=0.1,
    llm_top_k=100,
    # RAG Settings
    rag_enabled=True,
    rag_provider_name="agent-search",
    # Evaluation Settings
    n_few_shot=3,
    n_samples=100,
    evals_to_run="science_multiple_choice",
    *args,
    **kwargs,
):
    rag_interface = (
        RAGInterfaceManager.get_interface_from_args(
            RAGProviderName(rag_provider_name),
        )
        if rag_enabled
        else None
    )
    llm_interface = LLMInterfaceManager.get_interface_from_args(
        LLMProviderName(llm_provider_name),
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

    for eval in evals_to_run.split(","):
        logger.info(f"Running eval: {eval}")
        if eval == "science_multiple_choice":
            evaluator = ScienceMultipleChoiceEvaluator(
                llm_interface=llm_interface,
                rag_interface=rag_interface,
                n_few_shot=n_few_shot,
                n_samples=n_samples,
            )

        # TODO - Implement other evals

        logger.info(f"Instruction:\n\n{evaluator.instruction}")
        logger.info("Now building prompts...")
        evaluator.initialize_prompts()
        logger.info(f"Example Prompt:\n\n{evaluator.prompts[0]}")

        logger.info("Now generating completions...")
        counts = 0
        for i in tqdm(range(n_samples)):
            logger.debug(
                f"Processing sample {i} with prompt:\n{evaluator.prompts[i]}"
            )
            response = llm_interface.get_completion(
                prompt=evaluator.prompts[i],
                generation_config=llm_generation_config,
            )
            counts += int(evaluator.evaluate_response(response, i))
        logger.info(f"Final Accuracy={(counts) / (i + 1)}")


if __name__ == "__main__":
    fire.Fire(main)
