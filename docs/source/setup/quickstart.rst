.. _synthesizer_quickstart:

Synthesizer Quickstart
======================

Welcome to the Synthesizer quickstart guide! Synthesizer, or ΨΦ, is your portal to combining Retrieval-Augmented Generation (RAG) with large language models (LLMs) like OpenAI's models, Anthropic, HuggingFace, and vLLM.

This guide will introduce you to:

- Generating data tailored to your needs.
- Using the RAG provider interface.
- Creating RAG-enhanced textbooks.
- Evaluating your RAG pipeline.


Let's get started!

Setting Up Your Environment
---------------------------

Before you start, ensure you've installed Synthesizer:

.. code-block:: bash

    pip install sciphi-synthesizer

For additional details, refer to the `installation guide <https://sciphi.readthedocs.io/en/latest/setup/installation.html>`_.

Instantiate Your LLM and RAG Provider
-------------------------------------

Here's how you can use Synthesizer to quickly set up and retrieve chat completions, without diving deep into intricate configurations:

.. code-block:: python
    
    # Requires a valid SCIPHI_API_KEY in env ...

    # Imports
    from synthesizer.core import LLMProviderName, RAGProviderName
    from synthesizer.interface import (
        LLMInterfaceManager,
        RAGInterfaceManager,
    )
    from synthesizer.llm import GenerationConfig

    # RAG Provider Settings
    rag_interface = RAGInterfaceManager.get_interface_from_args(
        RAGProviderName(rag_provider_name),
        api_base=rag_api_base,
        limit_hierarchical_url_results=rag_limit_hierarchical_url_results,
        limit_final_pagerank_results=rag_limit_final_pagerank_results,
    )
    rag_context = rag_interface.get_rag_context(query)

    # LLM Provider Settings
    llm_interface = LLMInterfaceManager.get_interface_from_args(
        LLMProviderName("openai"),
    )

    generation_config = GenerationConfig(
        model_name=llm_model_name,
        max_tokens_to_sample=llm_max_tokens_to_sample,
        temperature=llm_temperature,
        top_p=llm_top_p,
        # other generation params here ...
    )

    formatted_prompt = rag_prompt.format(rag_context=rag_context)
    completion = llm_interface.get_completion(
        formatted_prompt, generation_config
    )
    print(completion)

    ### Output:
    # Fermat's Last Theorem was proven by British mathematician Andrew Wiles in 1994 (Wikipedia). Wiles's proof was based on a special case of the modularity theorem for elliptic curves, along with Ribet's theorem (Wikipedia). The modularity theorem and Fermat's Last Theorem were previously considered inaccessible to proof by contemporaneous mathematicians (Wikipedia). However, Wiles's proof provided a solution to Fermat's Last Theorem, which had remained unproved for over 300 years (PlanetMath). Wiles's proof is widely accepted and has been recognized with numerous awards, including the Abel Prize in 2016 (Wikipedia).

    # It is important to note that Wiles's proof of Fermat's Last Theorem is a mathematical proof and not related to the science fiction novel "The Last Theorem" by Arthur C. Clarke and Frederik Pohl (Wikipedia). The novel is a work of fiction and does not provide a real mathematical proof for Fermat's Last Theorem (Wikipedia). Additionally, there have been other attempts to prove Fermat's Last Theorem, such as Sophie Germain's approach, but Wiles's proof is the most widely accepted and recognized (Math Stack Exchange).
