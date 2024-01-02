from synthesizer.core import LLMProviderName, RAGProviderName
from synthesizer.interface import (
    LLMInterfaceManager,
    RAGInterfaceManager,
)
from synthesizer.llm import GenerationConfig
import fire

# Note, it is understood that the prompt has an issue with redundancy. This will be addressed shortly.
PROMPT = """
### Instruction:

### Instruction:

Prompt:
{query}

Context:
{rag_context}

Prompt:
{query}

Your task is to write a response to the given prompt. If the prompt is clearly a question, then answer it directly. If the prompt is a statement, then the most important related context that you have been given. WRITE THREE DISTINCT SECTIONS  `### My Work`, `### My Answer`, and `### My Further Considerations` as shown below. ONLY USE THE PROVIDED CONTEXT to answer the question, and if the context is insufficient then answer with \"Insufficient Context\". Be sure to include at least 5 distinct sources in your final answer.\n\n### My Work\n- **Valid Premise Check:** Ensure that the question contains a valid premise before answering.\n- **Contextual Analysis:** Think step-by-step about the provided context to identify the most important and/or relevant themes covered in the provided information. Be sure to consider at least 5 distinct sources.\n\n### My Answer\n- **Answer with Inline Numbered Citations:** Provide a response in two to three paragraphs, including inline citations to the most relevant evidence from the provided context. Use the following format for inline citations: `[1]`, `[2]`, `[3]`, etc.\n\n### My Further Considerations\n- **Implications and Follow-Ups:** Consider the implications of the question and answer. Identify any related follow-up questions or considerations that come to mind. \n- **Queries** Provide a comma-separated list of Google queries that you would like to see answered in the future.\n\nBegin your work now:\n \n 

### Response:

### Response:

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
        # rag_prompt="### Instruction:\nYour task is to use the context which follows to answer the question with a two paragraph line-item cited response:\n<context>{rag_context}</context>\nBegin your two paragraph answer with line-item citations now:### Response:\n",
        # rag parameters
        rag_provider_name="agent-search",
        rag_api_base="https://api.sciphi.ai",
        rag_limit_hierarchical_url_results="50",
        rag_limit_final_pagerank_results="20",
        # llm parameters
        llm_provider_name="sciphi",
        llm_model_name="SciPhi/SciPhi-SearchAgent-Alpha-7B",
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
        completion = llm_interface.get_completion(
            formatted_prompt, generation_config
        ).replace("</s>", "")
        print(json.loads(completion))

        ### Output:
        # {"summary": "\nFermat's Last Theorem is a significant result in number theory, stating that for any natural number n greater than 2, there are no solutions to the equation \\(a^n + b^n = c^n\\) where \\(a\\), \\(b\\), and \\(c\\) are positive integers [5]. The theorem was first proposed by Pierre de Fermat in the margins of his copy of Diophantus's \"Arithmetica\" in the 17th century, but it remained unproved for over three centuries [8]. The first case of the theorem to be proven was by Fermat himself for \\(n = 4\\), using a method of infinite descent [9]. Leonhard Euler later provided a proof for the case \\(n = 3\\), although his initial proof contained errors that were later corrected [9].\n\nThe theorem was finally proven in its entirety in 1995 by British mathematician Andrew Wiles, using sophisticated mathematical tools and techniques that were not available during Fermat's lifetime [10]. This breakthrough marked the end of a long period of mathematical speculation and the resolution of a major historical puzzle in mathematics [10]. The proof of Fermat's Last Theorem has been hailed as one of the most significant achievements in the history of mathematics, demonstrating the power of modern mathematical methods and the persistence of mathematical inquiry over centuries [10].\n\n", "other_queries": ["Details of Fermat's Last Theorem proof", "Historical impact of Fermat's Last Theorem", "Contributions of Andrew Wiles to mathematics", "Techniques used in the proof of Fermat's Last Theorem", "Evolution of number theory post-Fermat's Last Theorem"]}


if __name__ == "__main__":
    fire.Fire(RagDemo)
