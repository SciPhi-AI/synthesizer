Welcome to Synthesizer 💡
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



A multi-purpose LLM framework for inference, RAG, and data creation.

With Synthesizer, you can:

* Leverage **Retrieval-Augmented Generation (RAG)** for better accuracy and efficiency.
   - Turnkey integration with SciPhi's AgentSearch.
* Generate truthful datasets using various LLMs, supporting **Anthropic**, **OpenAI**, **vLLM**.
* Custom tailored data for applications such as LLM training, RAG, and beyond.
   - For ex., create RAG-grounded textbooks.

Quick and easy setup:

* Installation with pip: ``pip install sciphi``
* Optional dependencies are available for extended functionality, such as ``sciphi[all_with_extras]`` for additional integrations.

Diverse Features:

* Seamlessly integrate multiple LLM and RAG providers like OpenAI, Anthropic, HuggingFace, and vLLM.
* Generate custom datasets and even full textbooks using synthesizers unique capabilities.
* Evaluate your RAG systems effectively with the synthesizer evaluation harness.
* Engage with the community on platforms like `Discord <https://discord.gg/j9GxfbxqAe>`_.

Developers can also instantiate their own LLM and RAG providers using the Synthesizer framework. The supported LLM providers include popular choices like OpenAI, Anthropic, HuggingFace, and vLLM. For specialized RAG capabilities, SciPhi offers the `AgentSearch API <https://agent-search.readthedocs.io/en/latest/api/main.html>`_ for comprehensive knowledge access.

You can use this format in your reStructuredText documentation, and it should render as a clickable link.
For a detailed setup guide, deeper feature exploration, and developer insights, refer to:

* `Example Textbook Generated with Synthesizer <https://github.com/SciPhi-AI/synthesizer/blob/main/synthesizer/data/sample/textbooks/Aerodynamics_of_Viscous_Fluids.md>`_
* `Library of Phi <https://github.com/SciPhi-AI/library-of-phi/>`_


Documentation
-------------

.. toctree::
   :maxdepth: 1
   :caption: Getting Started

   setup/installation
   setup/quickstart