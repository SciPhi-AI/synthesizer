# SciPhi [<span style="color:gold">ΨΦ</span>]: A Framework for LLM Powered Data


<p align="center">
<img width="716" alt="SciPhi Logo" src="https://github.com/emrgnt-cmplxty/sciphi/assets/68796651/c4192288-b5af-4ef8-9774-82b3bb5c8251">
</p>

SciPhi is a Python framework that enables the generation of high-quality synthetic data for LLM and/or human consumption. Key features include:

- **Configurable Data Generation:** Produce LLM-mediated datasets tailored to your needs.
- **The Library of Phi:** An AI-powered initiative that creates open-source textbooks.

## Community & Support

- Join our [Discord community](https://discord.gg/j9GxfbxqAe) for discussions and collaboration.
- For specialized inquiries, [email us](mailto:owen@emergentagi.com).

## Features

### Configurable Data Generation

Execute `runner.py` with various command-line arguments for customized data generation.

```bash
python sciphi/examples/basic_data_gen/runner.py --provider_name=openai --model_name=gpt-4 --log_level=INFO --batch_size=1 --num_samples=1 --output_file_name=example_output.jsonl --example_config=textbooks_are_all_you_need_basic_split
```

*Generates a single sample from GPT-4 using specified configurations.*

#### Command-Line Arguments

Refer to the README for a comprehensive list of arguments and their defaults. Noteworthy ones include `--provider`, `--model_name`, and `--temperature`.

### The Library of Phi

An initiative to democratize access to high-quality textbooks by employing AI techniques to craft factually accurate books.

#### Generating Textbooks

1. **Dry Run:**
   ```bash
   python sciphi/examples/library_of_phi/generate_textbook.py dry_run
   ```

2. **Default Textbook Generation:**
   ```bash
   python sciphi/examples/library_of_phi/generate_textbook.py run  --llm-provider=openai --llm_model_name=gpt-3.5-turbo --do-rag=False --textbook=Aerodynamics_of_Viscous_Fluids --filter_existing_books=False --log-level=debug
   ```

   [Sample Output](sciphi/data/library_of_phi/sample/Aerodynamics_of_Viscous_Fluids.md)

3. **Using Custom Table of Contents:** Draft and save as `textbook_name.yaml`, then place it in the specified directory.

4. **Incorporating RAG:** Enable the flag and set the appropriate `.env` variables.

*Note:* Ensure alignment with our specifications if using Wikipedia for RAG. Explore more examples [here](https://github.com/emrgnt-cmplxty/library_of_phi/tree/main).

## Getting Started

### Installation

1. Clone and navigate to the repository:
   ```bash
   git clone https://github.com/emrgnt-cmplxty/sciphi.git
   cd sciphi
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment:
   ```bash
   cp .env.example .env
   ```

### Requirements

- **Python:** 3.11 - 3.12

### Optional Dependencies

Install enhanced features using `pip install <package_name>`.

---

## License

Apache-2.0 License.

### Citation

If using SciPhi in your research, please cite:

```plaintext
@software{SciPhi,
author = {Colegrove, Owen},
doi = {Pending},
month = {09},
title = {{SciPhi}},
url = {https://github.com/emrgnt-cmplxty/sciphi},
year = {2023}
}
```