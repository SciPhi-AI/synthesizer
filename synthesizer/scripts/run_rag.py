import json
from synthesizer.core import LLMProviderName, RAGProviderName
from synthesizer.interface import (
    LLMInterfaceManager,
    RAGInterfaceManager,
)
from synthesizer.llm import GenerationConfig
import fire

PROMPT = """
### Instruction:

Query:
{query}

Search Results:
{rag_context}

Query:
{query}

### Response:
{{"summary":
"""


class RagDemo:
    """A demonstration of agent-search + synthesizer RAG pipeline."""

    def __init__(self):
        try:
            import synthesizer
        except ImportError as e:
            raise ImportError(
                f"Demo run_rag.py failed with {e}. Please run pip install sciphi-synthesizer before attempting to run this script."
            )

    def run(
        self,
        query="What is a quantum field theory in curved space time?",
        rag_provider_name="agent-search",
        rag_api_base="https://api.sciphi.ai",
        # llm parameters
        llm_provider_name="sciphi",
        llm_model_name="SciPhi/Sensei-7B-V1",
        llm_max_tokens_to_sample=1_024,
        llm_temperature=0.1,
        llm_top_p=0.95,
    ):
        # RAG Provider Settings
        rag_interface = RAGInterfaceManager.get_interface_from_args(
            RAGProviderName(rag_provider_name),
            api_base=rag_api_base,
            # limit_hierarchical_url_results=rag_limit_hierarchical_url_results,
            # limit_final_pagerank_results=rag_limit_final_pagerank_results,
        )
        rag_context = rag_interface.get_rag_context(query)

        # LLM Provider Settings
        llm_interface = LLMInterfaceManager.get_interface_from_args(
            LLMProviderName(llm_provider_name),
        )

        generation_config = GenerationConfig(
            model_name=llm_model_name,
            max_tokens_to_sample=llm_max_tokens_to_sample,
            temperature=llm_temperature,
            top_p=llm_top_p,
            # other generation params here ...
        )

        formatted_prompt = PROMPT.format(rag_context=rag_context, query=query)
        completion = '{"summary":' + llm_interface.get_completion(
            formatted_prompt, generation_config
        ).replace("</s>", "")
        print(json.loads(completion))

        ### Output:
        # {"summary": "\nFermat's Last Theorem is a significant result in number theory, stating that for any natural number n greater than 2, there are no solutions to the equation \\(a^n + b^n = c^n\\) where \\(a\\), \\(b\\), and \\(c\\) are positive integers [5]. The theorem was first proposed by Pierre de Fermat in the margins of his copy of Diophantus's \"Arithmetica\" in the 17th century, but it remained unproved for over three centuries [8]. The first case of the theorem to be proven was by Fermat himself for \\(n = 4\\), using a method of infinite descent [9]. Leonhard Euler later provided a proof for the case \\(n = 3\\), although his initial proof contained errors that were later corrected [9].\n\nThe theorem was finally proven in its entirety in 1995 by British mathematician Andrew Wiles, using sophisticated mathematical tools and techniques that were not available during Fermat's lifetime [10]. This breakthrough marked the end of a long period of mathematical speculation and the resolution of a major historical puzzle in mathematics [10]. The proof of Fermat's Last Theorem has been hailed as one of the most significant achievements in the history of mathematics, demonstrating the power of modern mathematical methods and the persistence of mathematical inquiry over centuries [10].\n\n", "other_queries": ["Details of Fermat's Last Theorem proof", "Historical impact of Fermat's Last Theorem", "Contributions of Andrew Wiles to mathematics", "Techniques used in the proof of Fermat's Last Theorem", "Evolution of number theory post-Fermat's Last Theorem"]}</s>


if __name__ == "__main__":
    fire.Fire(RagDemo)
