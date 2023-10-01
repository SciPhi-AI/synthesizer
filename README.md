# **SciPhi [ΨΦ]: A Framework for Breaking LLM Scaling Laws**

## **Overview**

SciPhi is a Python package offering:
- Configurable generation of LLM-mediated synthetic training/tuning data.
- Seamless LLM-mediated evaluation of model output.

<p align="center">
<img width="524" alt="Screenshot 2023-09-18 at 9 53 55 AM" src="https://github.com/emrgnt-cmplxty/SciPhi/assets/68796651/9731f891-1d99-432a-aaec-37916bc6362f">
</p>

## **Questions?**

- Join our [Discord community](https://discord.gg/j9GxfbxqAe).
- For direct inquiries, [email me](mailto:owen@emergentagi.com).
- New to SciPhi? Start with our [tutorial](https://substack.com/inbox/post/137197905).

## **Installation**

```bash
# Clone the repository
git clone https://github.com/emrgnt-cmplxty/sciphi.git
cd sciphi

# Install dependencies
# Install poetry if you don't have it: pip3 install poetry
poetry install -E all

# Set up your environment
# Note: Modify the .env file as needed after copying
cp .env.example .env && vim .env
```

### Requirements

- Python: >= 3.11 and < 3.12
- Poetry: For package management

### Optional Features

Install optional dependencies for enhanced features:

```bash
poetry install -E <extra_name>
```

Options include:
- `anthropic_support`: For Anthropic models.
- `hf_support`: With the HuggingFace package for diverse model access.
- `openai_support`: For OpenAI models.
- `vllm_support`: For VLLM, aiding fast inference.
- `llama_index_support`: For LlamaIndex, enhancing grounded synthesis.
- `chroma_support`: For Chroma support in large vector databases.
- `all`: Includes all dependencies (excluding `vllm`, which needs separate installation).
- `all_with_cuda`: Everything.

## **Usage**

### **Library of Phi Generation**

**Overview:**  
The Library of Phi is an initiative sponsored by SciPhi. Its primary goal is to democratize access to high-quality textbooks. The project utilizes AI-driven techniques to generate textbooks by processing information from the MIT OCW course webpages.


**Workflow:**  
The workflow encompasses data scraping, data processing, YAML configuration creation, and RAG execution over Wikipedia, with intermittent work done by LLMs.

1. Scrape MIT OCW Course Webpages.
2. Extract Syllabi.
3. Formulate Table of Contents.
4. Craft Textbooks.

#### **Generating the default Textbook:**

```bash
poetry run python sciphi/examples/library_of_phi/generate_textbook.py run --do-wiki=False --textbook=Introduction_to_Deep_Learning
```

#### **Using a Custom Table of Contents:**

1. Draft a table of contents and save as `textbook_name.yaml`.
2. Place it in `sciphi/examples/library_of_phi/raw_data/table_of_contents`.
3. Format similarly to `Introduction_to_Deep_Learning.yaml`.

#### **Incorporating RAG over Wikipedia:**

1. Enable the `--do-wiki` flag: `True`.
2. In `.env`, set:
   - `WIKI_SERVER_URL`
   - `WIKI_SERVER_USERNAME`
   - `WIKI_SERVER_PASSWORD`

**Output**:  
Generated textbooks reside in:  
`[Your Working Directory]/sciphi/examples/library_of_phi/raw_data/created_textbooks`

**Note**: The Wikipedia embeddings server is private but will be public soon. Meanwhile, ensure your configuration aligns with our specifications.

---

### Replicating Full Table of Contents Generation

**Step 0**: Scrape MIT OCW for course details.

```bash
poetry run python sciphi/examples/library_of_phi/raw_data/ocw_scraper.py scrape
```

**Step 1**: Convert scraped data into 'draft' syllabi YAMLs.

```bash
poetry run python sciphi/examples/library_of_phi/gen_step_1_draft_syllabi.py run
```

**Step 2**: Refine the draft YAML into the finalized syllabi.

```bash
poetry run python sciphi/examples/library_of_phi/gen_step_2_clean_syllabi.py run
```

**Step 3**: Transition the syllabi to a table of contents.

```bash
poetry run python sciphi/examples/library_of_phi/gen_step_3_table_of_contents.py run
```

### Customizable Runner Script

For flexible applications, execute the relevant `runner.py` with various command-line arguments.

```bash
poetry run python sciphi/examples/basic_data_gen/runner.py --provider_name=openai --model_name=gpt-4 --log_level=INFO --batch_size=1 --num_samples=1 --output_file_name=example_output.jsonl --example_config=textbooks_are_all_you_need_basic_split
```

### Command-Line Arguments

See arguments and their default values in the README. Notable ones include `--provider`, `--model_name`, and `--temperature`.

### Example Generated Data

<p align="center">
<img width="776" alt="Screenshot 2023-09-17 at 11 11 18 PM" src="https://github.com/emrgnt-cmplxty/SciPhi/assets/68796651/8f1ef11d-cd37-4fc7-a7a0-a1e0159ba4a3">
</p>

## Development

Use SciPhi to craft synthetic data for a given LLM provider. Check the provided code for an example.

### License

Licensed under the Apache-2.0 License.

### Referenced Datasets

1. [Python Synthetic Textbooks](https://huggingface.co/datasets/emrgnt-cmplxty/sciphi-python-textbook/viewer/default/train)
2. [Textbooks are all you need](https://huggingface.co/datasets/emrgnt-cmplxty/sciphi-textbooks-are-all-you-need)

### Citations

1. [WizardCoder: Empowering Code Large Language Models with Evol-Instruct](https://arxiv.org/abs/2306.08568)
2. [Textbooks Are All You Need](https://arxiv.org/abs/2306.11644)

## Citation

If using SciPhi in academic work, please cite:

```
@software{Emergent_AGI_SciPhi,
author = {Colegrove, Owen},
doi = {Pending},
month = {09},
title = {{SciPhi}},
url = {https://github.com/emrgnt-cmplxty/sciphi},
year = {2023}
}
```