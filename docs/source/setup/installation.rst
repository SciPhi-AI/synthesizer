.. _sciphi_installation:

Installation for SciPhi
=====================================================

SciPhi is a powerful knowledge engine that integrates with multiple LLM providers and RAG providers, allowing for customizable data creation, retriever-augmented generation, and even textbook generation.

Requirements
------------

- **Python**: `>=3.9,<3.12`
- **Libraries**: (Please refer to the README for a detailed list)

Fast Installation with pip
--------------------------

Installing SciPhi is as simple as using pip:

.. code-block:: console

   $ pip install sciphi

Optional Extra Dependencies
---------------------------

For complete advanced features and provider support:

.. code-block:: console

   $ pip install 'sciphi[all_with_extras]'

Setting Up Your Environment
---------------------------

After installation, set up your environment to link with supported LLM providers:

.. code-block:: console

   $ cd your_working_directory
   $ nano .env  # Adjust the .env file with your specific configurations.

Here is an example of the configuration in the `.env` file:

.. code-block:: bash
   # To use SciPhi as a provider:
   SCIPHI_API_KEY=your_sciphi_api_key

   # Other providers in SciPhi:
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   HF_TOKEN=your_huggingface_token
   VLLM_API_KEY=your_vllm_api_key
   RAG_API_KEY=your_rag_server_api_key
   RAG_API_BASE=your_rag_api_base_url

.. note::
   Make sure to save and exit the file after making changes.

Development Setup
-----------------

To set up SciPhi for development:

.. code-block:: console

   $ git clone https://github.com/SciPhi-AI/sciphi.git
   $ cd sciphi
   $ pip3 install poetry  # If you do not have Poetry installed.
   $ poetry install # Can use `pip install -e .`` instead.
   $ poetry install -E all_with_extras

Licensing and Acknowledgment
---------------------------

SciPhi is licensed under the Apache-2.0 License.
