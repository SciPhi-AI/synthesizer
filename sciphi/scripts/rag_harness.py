import logging
import os

import dotenv
import fire
from tqdm import tqdm

from sciphi.core import LLMProviderName, RAGProviderName
from sciphi.eval.rag import ScienceMultipleChoiceEvaluator
from sciphi.interface import LLMInterfaceManager, RAGInterfaceManager

# Load environment variables
dotenv.load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(
    # LLM Settings
    llm_provider_name="openai",
    llm_model_name="gpt-3.5-turbo",
    llm_max_tokens_to_sample=32,
    llm_temperature=0.1,
    llm_top_k=100,
    # RAG Settings
    rag_provider_name="sciphi-wiki",
    rag_enabled=True,
    rag_api_base=None,
    rag_api_key=None,
    rag_max_context=2048,
    rag_top_k=10,
    # Evaluation Settings
    n_few_shot=3,
    n_samples=100,
    evals_to_run="science_multiple_choice",
    **kwargs,
):
    llm_interface = LLMInterfaceManager.get_interface_from_args(
        provider_name=LLMProviderName(llm_provider_name),
        model_name=llm_model_name,
        # Additional args
        max_tokens_to_sample=llm_max_tokens_to_sample,
        temperature=llm_temperature,
        top_k=llm_top_k,
        # Used for re-routing requests to a remote vLLM server
        server_base=kwargs.get("llm_server_base", None),
    )

    rag_interface = (
        RAGInterfaceManager.get_interface_from_args(
            provider_name=RAGProviderName(rag_provider_name),
            base=rag_api_base or os.environ.get("RAG_API_BASE"),
            token=rag_api_key or os.environ.get("RAG_API_KEY"),
            max_context=rag_max_context,
            top_k=rag_top_k,
        )
        if rag_enabled
        else None
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
                prompt=evaluator.prompts[i]
            )
            counts += int(evaluator.evaluate_response(response, i))
        logger.info(f"Final Accuracy={(counts) / (i + 1)}")


if __name__ == "__main__":
    fire.Fire(main)
