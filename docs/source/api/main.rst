# SciPhi API Documentation (in reStructuredText format)

SciPhi API Documentation
========================

Welcome to the SciPhi API documentation. Here, you'll find a detailed guide on how to use the different endpoints provided by the SciPhi service. This API allows you to interact with the powerful functionalities of the SciPhi codebase, bringing the power of large language models directly to your applications.

Endpoint Overview
-----------------

1. **Search**: This endpoint allows you to use the Retriever to fetch related documents from a given set of queries. Meta's `Contreiver` embeddings are used in this process. Currently just Wikipedia is embedded, but the goal is to scale this to a comprehensive database embedded via recent SOTA methods. 
2. **OpenAI Formatted LLM Request (v1)**: SciPhi models are served via an API that is compatible with the OpenAI API.

Detailed Endpoint Descriptions
------------------------------

Search Endpoint
~~~~~~~~~~~~~~~

- **URL**: ``/search``
- **Method**: ``POST``
- **Description**: This endpoint interacts with the Retriever module of the SciPhi codebase, allowing you to search for related documents based on the provided queries.

**Request Body**:
  - ``queries``: List of query strings for which related documents are to be retrieved.
  - ``top_k``: (Optional) The number of top related documents you wish to retrieve for each query.

**Response**: 
A list of lists containing Document objects, where each list corresponds to the related documents for each query.

**Example**:

.. code-block:: bash

   curl -X POST http://<api_url>/search \
       -H "Authorization: Bearer YOUR_API_KEY" \
       -d '{"queries": ["What is general relativity?", "Who is Albert Einstein?"], "top_k": 5}'

OpenAI API (v1) Endpoint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **URL**: ``/v1/{path:path}``
- **Method**: ``GET``, ``POST``, ``PUT``, ``DELETE``
- **Description**: This endpoint is designed to forward requests to another server, such as vLLM. It can act as a middleware, allowing you to utilize other services while managing access through the SciPhi API.

**Request Body**: 
The body should match the request format of the service to which you are forwarding the request.

**Response**: 
The response received from the forwarded service.

**Example**:

.. code-block:: bash

   curl -X POST https://api.sciphi.ai/v1/completion \
       -H "Authorization: Bearer YOUR_API_KEY" \
       -d '{"prompt": "Describe the universe.", ...}'


Alternatively, with the SciPhi framework, you may execute a generation as shown:


.. code-block:: python

    from sciphi.interface import LLMInterfaceManager, RAGInterfaceManager
    from sciphi.llm import GenerationConfig

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



API Key and Signup
------------------

To access the SciPhi API, you will need an API key. If you don't have one, you can sign up `here <https://www.sciphi.ai/signup>`_. Ensure you include the API key in your request headers as shown in the examples.