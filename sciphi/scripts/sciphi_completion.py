from dataclasses import fields, is_dataclass
from typing import Optional

import fire

from sciphi.core import LLMProviderName, RAGProviderName
from sciphi.interface.llm.sciphi_interface import SciPhiFormatter
from sciphi.interface.llm_interface_manager import (
    LLMInterfaceManager,
)
from sciphi.interface.rag_interface_manager import RAGInterfaceManager
from sciphi.llm import GenerationConfig


def filter_relevant_args(dataclass_type, args_dict):
    if not is_dataclass(dataclass_type):
        raise ValueError(f"{dataclass_type} is not a dataclass.")

    relevant_fields = {f.name for f in fields(dataclass_type)}
    return {k: v for k, v in args_dict.items() if k in relevant_fields}


def main(
    api_key: Optional[str] = None,
    server_base: str = "https://api.sciphi.ai/v1",
    rag_provider_name: str = "sciphi-wiki",
    rag_server_base: str = "https://api.sciphi.ai",
    rag_top_k: int = 10,
    rag_api_key: Optional[str] = None,
    query: str = "Who is the president of the United States?",
    **kwargs,
):
    rag_interface = RAGInterfaceManager.get_interface_from_args(
        provider_name=RAGProviderName(rag_provider_name),
        base=rag_server_base,
        api_key=rag_api_key or api_key,
        top_k=rag_top_k,
    )
    sciphi_llm = LLMInterfaceManager.get_interface_from_args(
        LLMProviderName("sciphi"),
        api_key=api_key,
        server_base=server_base,
        rag_interface=rag_interface,
    )

    completion_config = GenerationConfig(
        **filter_relevant_args(GenerationConfig, kwargs),
        stop_token=SciPhiFormatter.INIT_PARAGRAPH_TOKEN,
    )
    completion = sciphi_llm.get_completion(query, completion_config)
    print("completion = ", completion)


if __name__ == "__main__":
    fire.Fire(main)
