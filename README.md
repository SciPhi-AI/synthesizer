# SciPhi [<span style="color:gold">ΨΦ</span>]: A Framework for LLM Powered Data

<p align="center">
<img width="716" alt="SciPhi Logo" src="https://github.com/emrgnt-cmplxty/sciphi/assets/68796651/195367d8-54fd-4281-ace0-87ea8523f982">
</p>

SciPhi is a Python-based framework designed to facilitate the generation of high-quality synthetic data tailored for both Large Language Models (LLMs) and human users. This suite offers:

- **Configurable Data Generation:** Craft datasets mediated by LLMs according to your specifications.
- **Retriever-Augmented Generation (RAG) Integration:** Make use of an integrated RAG Provider API. Also, it comes bundled with an evaluation harness to ground your generated data to real-world datasets.
- **Textbook Generation Module:** A module to power the generation of RAG-augmented synthetic textbooks straight from a given table of contents.


---

## Fast Setup

Install SciPhi via `pip`:

### Base Installation:

```bash
pip install sciphi
```


### Optional Dependencies:

Install with specific optional support using extras:

- **Anthropic**: `'sciphi[anthropic_support]'`
- **HF (includes Torch)**: `'sciphi[hf_support]'`
- **Llama-CPP**: `'sciphi[llama_cpp_support]'`
- **Llama-Index**: `'sciphi[llama_index_support]'`
- **VLLM (includes Torch)**: `'sciphi[vllm_support]'`

### Recommended (All Optional Dependencies):

```bash
pip install 'sciphi[all_with_extras]'
```

Note: Depending on your shell, you might need to use quotes around the package name and extras to avoid globbing.

---

- Join our [Discord community](https://discord.gg/j9GxfbxqAe) for discussions and collaboration.
- For specialized inquiries, [email us](mailto:owen@sciphi.ai).

## Features

### Community & Support

- Engage with our vibrant community on [Discord](https://discord.gg/j9GxfbxqAe).
- For tailored inquiries or feedback, please [email us](mailto:owen@sciphi.ai).

### Textbook Generation (The Library of Phi)

This is an effort to democratize access to top-tier textbooks. By leveraging cutting-edge AI techniques, we aim to produce factual and high-quality educational materials. This can readily be extended to other domains, such as internal commercial documents.

#### Generating Textbooks

1. **Dry Run**:
   ```bash
   python sciphi/scripts/generate_textbook.py dry_run
   ```

2. **Default Textbook Generation**:
   ```bash
   python sciphi/scripts/generate_textbook.py run --textbook=Aerodynamics_of_Viscous_Fluids --rag-enabled=False --filter_existing_books=False --log-level=debug
   ```
   
   You may use the setting rag-enabled to toggle on/off RAG augmentation of the textbook. You may customize the RAG provider through additional arguments.

   See a [sample output here.](sciphi/data/library_of_phi/sample/Aerodynamics_of_Viscous_Fluids.md)

3. **Crafting with a Custom Table of Contents**: 

   Prepare your table of contents and save it as `textbook_name.yaml`. Then, move this file to the recommended directory.

4. **Activating RAG Functionality**: 

   Simply switch `rag-enabled` to `True`. Ensure you have the right `.env` variables set up, or provide CLI values for `rag_api_base` and `rag_api_key`.

_Important:_ To make the most out of grounding your data with Wikipedia, ensure your system matches our detailed specifications. We offer additional examples and resources [here](https://github.com/emrgnt-cmplxty/library_of_phi/tree/main).

### RAG Eval Harness

To measure the efficacy of your RAG pipeline, we provide a unique RAG evaluation harness.

#### Deploying the RAG Harness

1. **Initiate the Harness**:
   ```bash
   poetry run python sciphi/scripts/rag_harness.py --n-samples=100 --rag-enabled=True --evals_to_run="science_multiple_choice"
   ```

---

## Local Development

1. **Clone the Repository**:
   
   Begin by cloning the repository and stepping into the project directory:
   ```bash
   git clone https://github.com/emrgnt-cmplxty/sciphi.git
   cd sciphi
   ```

2. **Install the Dependencies**:

   Start by installing the primary requirements:
   ```bash
   pip install -r requirements.txt
   ```

   If you require further functionalities, consider the following:
   - For the developer's toolkit and utilities:
     ```bash
     pip install -r requirements-dev.txt
     ```

   - To encompass all optional dependencies:
     ```bash
     pip install -r requirements_all.txt
     ```

   Alternatively, to manage packages using Poetry:
   ```bash
   poetry install
   ```

     And for optional dependencies w/ Poetry:
     ```bash
     poetry install -E [all, all_with_extras]
     ```

3. **Setting Up Your Environment**:

   Begin by duplicating the sample environment file to craft your own:
   ```bash
   cp .env.example .env
   ```

   Next, use a text editor to adjust the `.env` file with your specific configurations. An example with `vim` is shown below:
   ```bash
   vim .env
   ```

   After entering your settings, ensure you save and exit the file.

---

## System Requirements

### Essential Packages:

- **Python Version**: `>=3.9,<3.12`

- **Required Libraries**:
  - `bs4`: `^0.0.1`
  - `fire`: `^0.5.0`
  - `openai`: `0.27.8`
  - `pandas`: `^2.1.0`
  - `python-dotenv`: `^1.0.0`
  - `pyyaml`: `^6.0.1`
  - `retrying`: `^1.3.4`
  - `sentencepiece`: `^0.1.99`
  - `torch`: `^2.1.0`
  - `tiktoken`: `^0.5.1`
  - `tqdm`: `^4.66.1`

### Supplementary Packages:

- **Anthropic Integration**:
  - `anthropic`: `^0.3.10`
- **Hugging Face Tools**:
  - `accelerate`: `^0.23.0`
  - `datasets`: `^2.14.5`
  - `transformers`: `^4.33.1`
- **Llama-Index**:
  - `llama-index`: `^0.8.29.post1`
- **Llama-CPP**:
  - `llama-cpp-python`: `^0.2.11`
- **VLLM Tools**:
  - `vllm`: `0.2.0`

---

## Licensing and Acknowledgment

This project is licensed under the [Apache-2.0 License](./LICENSE).

### Citing Our Work

If SciPhi plays a role in your research, we kindly ask you to acknowledge us with the following citation:

```plaintext
@software{SciPhi,
author = {Colegrove, Owen},
doi = {Pending},
month = {09},
title = {{SciPhi: A Framework for LLM Powered Data}},
url = {https://github.com/sciphi-ai/sciphi},
year = {2023}
}
```
