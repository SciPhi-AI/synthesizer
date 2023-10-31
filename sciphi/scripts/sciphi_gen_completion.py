from dataclasses import fields, is_dataclass
from typing import Optional

import fire

from sciphi.core import LLMProviderName, RAGProviderName
from sciphi.interface.llm.sciphi_interface import SciPhiFormatter
from sciphi.interface.llm_interface_manager import LLMInterfaceManager
from sciphi.interface.rag_interface_manager import RAGInterfaceManager
from sciphi.llm import GenerationConfig

msg_1 = """
Inside the box, no forces act upon the particle, so the time-independent Schrödinger equation is given by:

(-ħ^2 / (2m))(d^2ψ / dx^2) + V(x)ψ(x) = Eψ(x)

where ħ is the reduced Planck constant, m is the mass of the particle, V(x) is the potential energy of the particle, E is the energy of the particle, and ψ(x) is the wave function of the particle.   In the case of a particle in a box, the potential energy is zero inside the box, so the equation becomes:

(-ħ^2 / (2m))(d^2ψ / dx^2) = Eψ(x)
"""

msg_2 = """
It is given by:

(-γ^μ (∂ / ∂x^μ) + m)ψ(x) = 0

where γ^μ are the Dirac matrices, x^μ represents the position of the particle, m is the mass of the particle, and ψ(x) is the spinor representing the state of the particle.   
"""


def filter_relevant_args(dataclass_type, args_dict):
    if not is_dataclass(dataclass_type):
        raise ValueError(f"{dataclass_type} is not a dataclass.")

    relevant_fields = {f.name for f in fields(dataclass_type)}
    return {k: v for k, v in args_dict.items() if k in relevant_fields}


def main(
    query: str = "Who is the president of the United States?",
    llm_provider_name="sciphi",
    llm_model_name="SciPhi/SciPhi-Self-RAG-Mistral-7B-32k",
    llm_temperature=0.1,
    llm_top_k=100,
    llm_max_tokens_to_sample=256,
    llm_api_base: Optional[str] = None,
    llm_api_key: Optional[str] = None,
    llm_skip_special_tokens: bool = False,
    # RAG Settings
    rag_provider_name="sciphi-wiki",
    rag_enabled=True,
    rag_top_k=10,
    rag_api_base="https://api.sciphi.ai",
    rag_api_key=None,
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

    generation_config = GenerationConfig(
        temperature=llm_temperature,
        top_k=llm_top_k,
        max_tokens_to_sample=llm_max_tokens_to_sample,
        model_name=llm_model_name,
        skip_special_tokens=llm_skip_special_tokens,
        stop_token=SciPhiFormatter.INIT_PARAGRAPH_TOKEN,
    )

    conversation = [
        {
            "role": "system",
            "content": "You are a helpful and informative professor. You give long, accurate, and detailed explanations to student questions. You answer EVERY question that is given to you. You retrieve data multiple times if necessary.",
        },
        {
            "role": "user",
            "content": query,
            # "content": "Return Schrodinger's equation for a particle in a box.",
        },
        # {"role": "assistant", "content": msg_1},
        # {
        #     "role": "user",
        #     "content": "Excellent. Now, what about Dirac's equation for a free particle?",
        # },
        # {"role": "assistant", "content": msg_2},
        # {
        #     "role": "user",
        #     "content": query,
        # },
    ]
    # completion = llm_interface.get_completion(query, generation_config)
    completion = llm_interface.get_chat_completion(
        conversation, generation_config
    )
    print(f"Output Completion = {completion}")


if __name__ == "__main__":
    fire.Fire(main)
