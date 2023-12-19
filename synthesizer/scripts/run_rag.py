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
        )
        print(completion)

        ### Output:
        # Fermat's Last Theorem was proven by British mathematician Andrew Wiles in 1994 (Wikipedia). Wiles's proof was based on a special case of the modularity theorem for elliptic curves, along with Ribet's theorem (Wikipedia). The modularity theorem and Fermat's Last Theorem were previously considered inaccessible to proof by contemporaneous mathematicians (Wikipedia). However, Wiles's proof provided a solution to Fermat's Last Theorem, which had remained unproved for over 300 years (PlanetMath). Wiles's proof is widely accepted and has been recognized with numerous awards, including the Abel Prize in 2016 (Wikipedia).

        # It is important to note that Wiles's proof of Fermat's Last Theorem is a mathematical proof and not related to the science fiction novel "The Last Theorem" by Arthur C. Clarke and Frederik Pohl (Wikipedia). The novel is a work of fiction and does not provide a real mathematical proof for Fermat's Last Theorem (Wikipedia). Additionally, there have been other attempts to prove Fermat's Last Theorem, such as Sophie Germain's approach, but Wiles's proof is the most widely accepted and recognized (Math Stack Exchange).


if __name__ == "__main__":
    fire.Fire(RagDemo)
