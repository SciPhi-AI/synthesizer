.. _synthesizer_quickstart:

Synthesizer Quickstart
======================

Welcome to the Synthesizer quickstart guide! Synthesizer, or ΨΦ, is your portal to combining Retrieval-Augmented Generation (RAG) with large language models (LLMs) like OpenAI's models, Anthropic, HuggingFace, and vLLM.

This guide will introduce you to:

- Using the RAG provider interface.
- Evaluating your RAG pipeline.


Let's get started!

Setting Up Your Environment
---------------------------

Before you start, ensure you've installed Synthesizer:

.. code-block:: bash

    pip install sciphi-synthesizer

For additional details, refer to the `installation guide <https://sciphi.readthedocs.io/en/latest/setup/installation.html>`_.

Using Synthesizer
-----------------

1. **Generate synthetic question answer pairs**

   .. code-block:: bash

      export SCIPHI_API_KEY=MY_SCIPHI_API_KEY
      python -m synthesizer.scripts.data_augmenter run --dataset="wiki_qa"

   .. code-block:: bash

      tail augmented_output/config_name_eq_answer_question__dataset_name_eq_wiki_qa.jsonl
      { "formatted_prompt": "... ### Question:\nwhat country did wine originate in\n\n### Input:\n1. URL: https://en.wikipedia.org/wiki/History%20of%20wine (Score: 0.85)\nTitle:History of wine....",
      { "completion": Wine originated in the South Caucasus, which is now part of modern-day Armenia ...

2. **Evaluate RAG pipeline performance**

   .. code-block:: bash

      export SCIPHI_API_KEY=MY_SCIPHI_API_KEY
      python -m synthesizer.scripts.rag_harness --rag_provider="agent-search" --llm_provider_name="sciphi" --n_samples=25

   .. code-block:: bash
      ...
      INFO:__main__:Now generating completions...
      100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 100/100 [00:29<00:00,  3.40it/s]
      INFO:__main__:Final Accuracy=0.42

.. note::
    This is a basic introduction to Synthesizer. Check back later for more detailed and intricate documentation that delves deeper into advanced features and customization options.


Developing with Synthesizer
-------------------------------------

Here's how you can use Synthesizer to quickly set up and RAG augmented generation, without diving deep into intricate configurations:

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
        RAGProviderName("agent-search"),
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

    formatted_prompt = raw_prompt.format(rag_context=rag_context)
    completion = llm_interface.get_completion(
        formatted_prompt, generation_config
    )