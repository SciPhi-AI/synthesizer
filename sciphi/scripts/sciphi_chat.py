from dataclasses import fields, is_dataclass

import fire

from sciphi.interface import (
    SciPhiFormatter,
    SciPhiLLMInterface,
    SciPhiWikiRAGInterface,
)
from sciphi.llm import GenerationConfig


def filter_relevant_args(dataclass_type, args_dict):
    if not is_dataclass(dataclass_type):
        raise ValueError(f"{dataclass_type} is not a dataclass.")

    relevant_fields = {f.name for f in fields(dataclass_type)}
    return {k: v for k, v in args_dict.items() if k in relevant_fields}


def main(
    query: str = "Who is the president of the United States?",
    llm_model_name="SciPhi/SciPhi-Self-RAG-Mistral-7B-32k",
):
    rag_interface = SciPhiWikiRAGInterface()
    llm_interface = SciPhiLLMInterface(rag_interface)

    generation_config = GenerationConfig(
        model_name=llm_model_name,
        stop_token=SciPhiFormatter.INIT_PARAGRAPH_TOKEN,
    )

    # Example Conversation
    conversation = [
        {
            "role": "system",
            "content": "You are a helpful and informative professor. You give long, accurate, and detailed explanations to student questions. You answer EVERY question that is given to you. You retrieve data multiple times if necessary.",
        },
        {
            "role": "user",
            "content": "Who is the president of the United States?",
        },
        {
            "role": "assistant",
            "content": "Joe Biden is the current president of the United States.",
        },
        {
            "role": "user",
            "content": query,
        },
    ]

    completion = llm_interface.get_chat_completion(
        conversation, generation_config
    )
    print("Final Completion = ", completion)


if __name__ == "__main__":
    fire.Fire(main)
