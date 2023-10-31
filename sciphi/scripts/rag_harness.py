import logging
from typing import Optional

import dotenv
import fire
from tqdm import tqdm

from sciphi.core import LLMProviderName, RAGProviderName
from sciphi.eval.rag import ScienceMultipleChoiceEvaluator
from sciphi.interface import LLMInterfaceManager, RAGInterfaceManager
from sciphi.interface.llm.sciphi_interface import SciPhiFormatter
from sciphi.llm import GenerationConfig

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
    llm_api_base: Optional[str] = None,
    llm_api_key: Optional[str] = None,
    llm_skip_special_tokens: bool = False,
    # RAG Settings
    rag_provider_name="sciphi-wiki",
    rag_enabled=True,
    rag_api_base="https://api.sciphi.ai",
    rag_api_key=None,
    rag_top_k=10,
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
            api_base=rag_api_base or llm_api_base,
            api_key=rag_api_key or llm_api_key,
            top_k=rag_top_k,
        )
        if rag_enabled
        else None
    )
    llm_interface = LLMInterfaceManager.get_interface_from_args(
        LLMProviderName(llm_provider_name),
        api_key=llm_api_key,
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
        skip_special_tokens=llm_skip_special_tokens,
        stop_token=SciPhiFormatter.INIT_PARAGRAPH_TOKEN,
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
