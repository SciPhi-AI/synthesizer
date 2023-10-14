# **SciPhi [ΨΦ]: A Framework for Cata Creation**

<p align="center">
<img width="716" alt="Screenshot 2023-10-01 at 10 45 12 AM" src="https://github.com/emrgnt-cmplxty/sciphi/assets/68796651/c4192288-b5af-4ef8-9774-82b3bb5c8251">
</p>

**SciPhi** is an configurable Python framework designed to tackle the challenges of efficiently training powerful LLMs (Large Language Model) through synthetic data. At its core, SciPhi offers:

- **Configurable Data Generation**: Efficiently produce LLM-mediated synthetic training and tuning datasets tailored to your specific needs.
  
- **The Library of Phi**: An initiative to leverage AI-driven techniques to craft high-quality open source textbooks.

## **Getting Started & Support**

- Engage with our active [Discord community](https://discord.gg/j9GxfbxqAe) for discussions, troubleshooting, and collaboration.
  
- For specialized support or collaboration inquiries, feel free to [reach out directly](mailto:owen@emergentagi.com).

## **Library of Phi Generation**

**Introduction:**  
The Library of Phi is an initiative sponsored by SciPhi. Its primary goal is to democratize access to high-quality textbooks. The project utilizes AI-driven techniques to generate textbooks by processing combining raw information (such as table of contents) with unstructured data (such as Vector Databases) to generate high quality factually grounded textbooks.

#### **Optional - Validating Generation Pipeline:**

```bash
poetry run python sciphi/examples/library_of_phi/generate_textbook.py dry_run
```


#### **Generating the default Textbook:**

```bash
# Note, rather than passing arguments in the command line, you can modify the default settings in config/generation_settings/book_draft_settings.yml
poetry run python sciphi/examples/library_of_phi/generate_textbook.py run  --llm-provider=openai --llm_model_name=gpt-3.5-turbo --do-rag=False --textbook=Aerodynamics_of_Viscous_Fluids --filter_existing_books=False --log-level=debug
```

_[See the example output here](sciphi/data/library_of_phi/sample/Aerodynamics_of_Viscous_Fluids.md)_

#### **Using a Custom Table of Contents:**

1. Draft a table of contents and save as `textbook_name.yaml`.
2. Place it in `[Your Working Directory]/sciphi/data/library_of_phi/table_of_contents`.
3. Format identically to `Aerodynamics_of_Viscous_Fluids.yaml`.

#### **Incorporating RAG:**

1. Enable the `--do-rag` flag: `True`.
2. In `.env`, set:
   - `RAG_SERVER_URL`
   - `RAG_SERVER_USERNAME`
   - `RAG_SERVER_PASSWORD`

**Output**:  
Generated textbooks reside in:  
`[Your Working Directory]/sciphi/data/library_of_phi`

**Note**: The Wikipedia embeddings server is not yet public. Meanwhile, ensure your configuration aligns with our specifications if you wish to use wikipedia for RAG. If you would like to peruse more example textbooks, go [here](https://github.com/emrgnt-cmplxty/library_of_phi/tree/main).

## **Installation**

```bash
# Clone the repository
git clone https://github.com/emrgnt-cmplxty/sciphi.git
cd sciphi

# Install dependencies
# If you don't have poetry installed: pip3 install poetry
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
- `hf_support`: For diverse model access with the HuggingFace package.
- `openai_support`: For OpenAI models.
- `vllm_support`: For VLLM, aiding fast inference.
- `llamacpp_support`: For LlamaCPP, aiding gpu-poor inference. This hasn't been implemented perfectly, use the model_name parameter to specify the path to the model you want to use.
- `llama_index_support`: For LlamaIndex, enhancing grounded synthesis.
- `chroma_support`: For Chroma support in large vector databases.
- `all`: Includes all dependencies (excluding `vllm`, which needs separate installation).
- `all_with_cuda`: Everything.

---

### **Customizable Data Generation**

For fully configurable and flexible data generation, execute the relevant `runner.py` with various command-line arguments.

```bash
poetry run python sciphi/examples/basic_data_gen/runner.py --provider_name=openai --model_name=gpt-4 --log_level=INFO --batch_size=1 --num_samples=1 --output_file_name=example_output.jsonl --example_config=textbooks_are_all_you_need_basic_split
```

The above command will generate a single sample from GPT-4. This sample is generated using the `textbooks_are_all_you_need_basic_split` configuration, and the output is appended to `example_output.jsonl`. 

The long-term view of the SciPhi framework is to provide a training-feedback loop as shown below:

<p align="center">
<img width="524" alt="Screenshot 2023-09-18 at 9 53 55 AM" src="https://github.com/emrgnt-cmplxty/SciPhi/assets/68796651/9731f891-1d99-432a-aaec-37916bc6362f">
</p>

#### **Command-Line Arguments**

See arguments and their default values in the README. Notable ones include `--provider`, `--model_name`, and `--temperature`.

### License

Licensed under the Apache-2.0 License.

### Citations

1. [Textbooks Are All You Need](https://arxiv.org/abs/2306.11644)
2. [Textbooks Are All You Need II: Phi-1.5 Technical Report](https://arxiv.org/abs/2309.05463)

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
