.. _synthesizer_installation:

Installation
=====================================================

Synthesizer is a powerful LLM framework engine that integrates with multiple LLM providers and context providers, allowing for customizable data creation, retriever-augmented generation, and even textbook generation.

Requirements
------------

- **Python**: `>=3.9,<3.12`
- **Libraries**: (Please refer to the README for a detailed list)

Fast Installation with pip
--------------------------

Installing Synthesizer is as simple as using pip:

.. code-block:: console

   $ pip install sciphi-synthesizer

Optional Extra Dependencies
---------------------------

For complete advanced features and provider support:

.. code-block:: console

   $ pip install 'sciphi-synthesizer[all_with_extras]'

Development Setup
-----------------

To set up SciPhi for development:

.. code-block:: console

   $ git clone https://github.com/SciPhi-AI/synthesizer.git
   $ cd synthesizer
   $ pip3 install poetry  # If you do not have Poetry installed.
   $ poetry install # Can use `pip install -e .`` instead.
   $ poetry install -E all_with_extras

Licensing and Acknowledgment
---------------------------

Synthesizer is licensed under the Apache-2.0 License.
