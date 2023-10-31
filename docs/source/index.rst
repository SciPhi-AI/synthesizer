Welcome to SciPHi!
================

.. image:: https://github.com/emrgnt-cmplxty/sciphi/assets/68796651/195367d8-54fd-4281-ace0-87ea8523f982
   :width: 716
   :alt: SciPhi Logo
   :align: center

.. raw:: html

   <p style="text-align:center">
   <strong>AI's Knowledge Engine.
   </strong>
   </p>

   <p style="text-align:center">
   <script async defer src="https://buttons.github.io/buttons.js"></script>
   <a class="github-button" href="https://github.com/SciPhi-AI/sciphi" data-show-count="true" data-size="large" aria-label="Star">Star</a>
   <a class="github-button" href="https://github.com/SciPhi-AI/sciphi/subscription" data-icon="octicon-eye" data-size="large" aria-label="Watch">Watch</a>
   <a class="github-button" href="https://github.com/SciPhi-AI/sciphi/fork" data-icon="octicon-repo-forked" data-size="large" aria-label="Fork">Fork</a>
   </p>


SciPhi [ΨΦ]: AI's Knowledge Engine 💡
-----------------------------------------------------------------

SciPhi is a powerful knowledge engine tailored for LLM-based data generation and management.

With SciPhi, you can:

* Generate datasets using various LLMs, supporting **Anthropic**, **OpenAI**, **vLLM**, and **SciPhi**.
* Tap into the **Retriever-Augmented Generation (RAG)** for data anchoring to real-world sources.
   - Features like end-to-end cloud and local RAG knowledge engine APIs are underway!
* Custom tailor your data creation for applications such as LLM training, RAG, and beyond.
   - For instance, the in-built textbook module can generate RAG-enhanced textbooks from a given table of contents.

Quick and easy setup:

* Installation with pip: ``pip install sciphi``
* Optional dependencies are available for extended functionality, such as ``sciphi[vllm_support]`` for vLLM integration.

Diverse Features:

* Seamlessly integrate multiple LLM and RAG providers like SciPhi, OpenAI, Anthropic, HuggingFace, and vLLM.
* Generate custom datasets and even full textbooks using SciPhi's unique capabilities.
* Evaluate your RAG systems effectively with the SciPhi evaluation harness.
* Engage with the community on platforms like `Discord <https://discord.gg/j9GxfbxqAe>`_.

Developers can also instantiate their own LLM and RAG providers using the SciPhi framework. The supported LLM providers include popular choices like OpenAI, Anthropic, HuggingFace, and vLLM. For specialized RAG capabilities, SciPhi offers the **World Databasef API** for comprehensive database access.

For a detailed setup guide, deeper feature exploration, and developer insights, refer to:

* `SciPhi GitHub Repository <https://github.com/emrgnt-cmplxty/sciphi>`_
* `Example Textbook Generated with SciPhi <https://github.com/SciPhi-AI/sciphi/blob/main/sciphi/data/sample/textbooks/Aerodynamics_of_Viscous_Fluids.md>`_
* `ToC Used for Sample Textbook Generation <https://github.com/SciPhi-AI/sciphi/blob/main/sciphi/data/sample/table_of_contents/Aerodynamics_of_Viscous_Fluids.yaml>`_
* `Default Settings for Textbook Generation <https://github.com/SciPhi-AI/sciphi/blob/main/sciphi/config/generation_settings/textbook_generation_settings.yaml>`_
* `Library of SciPhi Books <https://github.com/SciPhi-AI/library-of-phi/>`_


Citing Our Work
---------------

If you're using SciPhi in your research or project, please cite our work:

.. code-block:: plaintext

   @software{SciPhi,
   author = {Colegrove, Owen},
   doi = {Pending},
   month = {09},
   title = {{SciPhi: A Framework for LLM Powered Data}},
   url = {https://github.com/sciphi-ai/sciphi},
   year = {2023}
   }

Documentation
-------------

.. toctree::
   :maxdepth: 1
   :caption: Getting Started

   setup/installation
   setup/quickstart

.. toctree::
   :maxdepth: 1
   :caption: API

   api/main