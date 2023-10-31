SciPhi API Documentation
========================

Welcome to the SciPhi API documentation. Here, you'll find a detailed guide on how to use the different endpoints provided by the SciPhi service. This API allows you to interact with the powerful functionalities of the SciPhi codebase and associated AI. SciPhi looks to become a powerful tool for exploring the world's knowledge, and we hope you enjoy using it!

Endpoint Overview
-----------------

1. **Search**: This endpoint allows you to fetch related documents based on a set of queries. The documents are retrieved by re-ranked similarity search over embeddings produced by the `facebook/contriever <https://huggingface.co/facebook/contriever>`_. As of now, only Wikipedia is embedded, but there are plans to expand this to a more comprehensive corpus using state-of-the-art embedding methods.
2. **OpenAI Formatted LLM Request (v1)**: SciPhi models are served via an API that is compatible with the OpenAI API.

Detailed Endpoint Descriptions
------------------------------

Search Endpoint
~~~~~~~~~~~~~~~

- **URL**: ``/search``
- **Method**: ``POST``
- **Description**: This endpoint interacts with the Retriever module of the SciPhi codebase, allowing you to search for related documents based on the provided queries.

**Request Body**:
  - ``queries``: A list of query strings for which related documents should be retrieved.
  - ``top_k``: (Optional) The number of top related documents you wish to retrieve for each query.

**Response**: 
A list of lists containing Document objects, where each list corresponds to the related documents for a specific query.

**Example**:

.. code-block:: bash

   curl -X POST https://api.sciphi.ai/search \
        -H "Authorization: Bearer $SCIPHI_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"queries": ["What is general relativity?", "Who is Albert Einstein?"], "top_k": 5}'

This request queries the SciPhi World Database. The expected response is:

.. code-block:: none

    [[{"id":14678539,"title":"General Relativity and Gravitation","text":"General Relativity and Gravitation General Re ...


SciPhi v1 Endpoints
~~~~~~~~~~~~~~~~~~~

SciPhi adheres to the API specification of OpenAI's API, allowing compatibility with any application designed for the OpenAI API. Below is an example curl command:

**Example**:

.. code-block:: bash

curl https://api.sciphi.ai/v1/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 55c51253002ed4f7d1dd3afbe2a72635" \
  -d '{
     "model": "SciPhi/SciPhi-Self-RAG-Mistral-7B-32k",
     "prompt": "Say this is a test.",
     "temperature": 0.7
   }'


After executing the above request with the SciPhi/SciPhi-Self-RAG-Mistral-7B-32k model, the expected response is:

.. code-block:: json

{
    "id":"cmpl-f03f53c15a174ffe89bdfc83507de7a9",
    "object":"text_completion",
    "created":1698730137,
    "model":"SciPhi/SciPhi-Self-RAG-Mistral-7B-32k",
    "choices":[
        {
            "index":0,
            "text":"This is a test.",
            "logprobs":null,
            "finish_reason":"length"
        }
    ],
    "usage":
        {
            "prompt_tokens":7,
            "total_tokens":23,
            "completion_tokens":16
        }
}                                                                                                                                                                           (base) ocolegrove@MacBook-Pro-5 sciphi-core % 

API Key and Signup
------------------

To access the SciPhi API, you need an API key. If you don't possess one, you can sign up `here <https://www.sciphi.ai/signup>`_. Ensure you include the API key in your request headers as shown in the examples.
