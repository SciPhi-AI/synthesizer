.. _sciphi_quickstart:

SciPhi Quickstart
=================

Welcome to the SciPhi quickstart guide! SciPhi, or ΨΦ, is your portal to using large language models (LLMs) like OpenAI's models, Anthropic, HuggingFace, and vLLM, combined with the power of Retriever-Augmented Generation (RAG).

This guide will introduce you to:
- Generating data tailored to your needs.
- Using the RAG provider interface.
- Creating RAG-enhanced textbooks.
- Evaluating your RAG pipeline.

Let's get started!

Setting Up Your Environment
---------------------------

Before you start, ensure you've installed SciPhi:

.. code-block:: bash

    pip install sciphi

For additional details, refer to the `installation guide <https://sciphi.readthedocs.io/en/latest/setup/installation.html>`_.

Instantiate Your LLM and RAG Provider
-------------------------------------

Here's how you can use SciPhi to quickly set up and retrieve chat completions, without diving deep into intricate configurations:

.. code-block:: python

    from sciphi.interface import (
        SciPhiFormatter,
        SciPhiLLMInterface,
        SciPhiWikiRAGInterface,
    )

    # SciPhi RAG Interface
    # Supports calls like `contexts = rag_interface.get_contexts(query)`
    rag_interface = SciPhiWikiRAGInterface()

    # SciPhi LLM Interface
    llm_interface = SciPhiLLMInterface(rag_interface)

    # Initializing the conversation
    query: str = "Who is the president of the United States?"
    conversation = []
    conversation.append({"role": "user", "content": query})

    # Define generation configuration
    generation_config = GenerationConfig(
        model_name=llm_model_name,
        stop_token=SciPhiFormatter.INIT_PARAGRAPH_TOKEN,
        # Pass in any other desired generation settings here
    )

    # Get the chat completion
    completion = llm_interface.get_chat_completion(
        conversation, generation_config
    )

    print(completion)
    # Expected output: The current President of the United States is Joe Biden.

---

Here's a more advanced example of how you can utilize SciPhi to work with configurably with available LLM and RAG providers:

.. code-block:: python

    from sciphi.core import LLMProviderName, RAGProviderName
    from sciphi.interface import LLMInterfaceManager, RAGInterfaceManager
    from sciphi.llm import GenerationConfig

    # Define your parameters here...

    # RAG Provider Settings
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

    # LLM Provider Settings
    llm_interface = LLMInterfaceManager.get_interface_from_args(
        LLMProviderName(llm_provider_name),
        api_key=llm_api_key,
        api_base=llm_api_base,
        rag_interface=rag_interface,
        model_name=llm_model_name,
    )

    # Set up typical LLM generation settings
    completion_config = GenerationConfig(
        temperature=llm_temperature,
        top_k=llm_top_k,
        max_tokens_to_sample=llm_max_tokens_to_sample,
        model_name=llm_model_name,
        skip_special_tokens=llm_skip_special_tokens,
        stop_token=SciPhiFormatter.INIT_PARAGRAPH_TOKEN,
    )

    # Get the completion for a prompt
    completion = llm_interface.get_completion(prompt, generation_config)

    # Continue with your process...

This example showcases the flexibility and power of SciPhi, allowing you to seamlessly integrate various LLM and RAG providers into your applications.


Generating Completions with SciPhi
---------------------------

SciPhi supports multiple LLM providers (e.g. OpenAI, Anthropic, HuggingFace, and vLLM) and RAG providers (e.g. SciPhi). To run an example completion with SciPhi the code shown above, execute:

```bash
python -m sciphi.scripts.sciphi_gen_completion -llm_provider_name=sciphi --llm_api_key=YOUR_SCIPHI_API_KEY --llm_api_base=https://api.sciphi.ai/v1 --rag_api_base=https://api.sciphi.ai --llm_model_name=SciPhi/SciPhi-Self-RAG-Mistral-7B-32k --query="Write a few paragraphs on general relativity. Include the mathematical definition of Einsteins field equation in your writeup."
```

Generating Data with SciPhi
---------------------------

To generate data tailored to your specifications, you can use the provided scripts. For instance, to generate a dataset with a desired number of samples:

.. code-block:: bash

    python -m sciphi.scripts.data_augmenter --config-path=$PWD/sciphi/config/prompts/question_and_answer.yaml --config_name=None --n_samples=1


Inspecting the output:

.. code-block:: bash

    {"question": "What is the reaction called when alcohol and carboxylic acids react?", "answer": "Fischer esterification"}
    ...
    {"question": "Are tertiary alcohols resistant to oxidation?", "answer": "Yes"}


This command can be readily expanded to other configurations.

RAG-Enhanced Textbooks
----------------------

With SciPhi, you can generate textbooks with the assistance of RAG. To perform a dry-run:

.. code-block:: bash

    python -m sciphi.scripts.textbook_generator dry_run --toc_dir=sciphi/data/sample/table_of_contents --rag-enabled=False

To generate a textbook:

.. code-block:: bash

    python -m sciphi.scripts.textbook_generator run --toc_dir=sciphi/data/sample/table_of_contents --rag-enabled=False --filter_existing_books=False

You can also use a custom table of contents:

.. code-block:: bash

    python -m sciphi.scripts.textbook_generator run --toc_dir=toc --output_dir=books --data_dir=$PWD

RAG Evaluation
--------------

Measure the efficacy of your RAG pipeline using SciPhi's evaluation harness:

.. code-block:: bash

    python -m sciphi.scripts.rag_harness --n-samples=100 --rag-enabled=True --evals_to_run="science_multiple_choice"

This will evaluate your RAG over a set of questions and report the final accuracy.


Wrapping Up
-----------

Congratulations! You've now been introduced to the core functionalities of SciPhi. This is just the beginning; delve deeper into the documentation, explore the community on Discord, or reach out for tailored inquiries. Happy modeling!