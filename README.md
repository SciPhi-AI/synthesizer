# SciPhi [<span style="color:gold">ΨΦ</span>]: A Framework for LLM Powered Data

<p align="center">
<img width="716" alt="SciPhi Logo" src="https://github.com/emrgnt-cmplxty/sciphi/assets/68796651/195367d8-54fd-4281-ace0-87ea8523f982">
</p>

SciPhi is a Python framework that enables the generation of high-quality synthetic data for LLM and/or human consumption. Key features include:

- **Configurable Data Generation:** Produce LLM-mediated datasets tailored to your needs.
- **RAG Grounding**
- **Textbook Generation**

## Community & Support

- Join our [Discord community](https://discord.gg/j9GxfbxqAe) for discussions and collaboration.
- For specialized inquiries, [email us](mailto:owen@sciphi.ai).

## Features

### Textbook Generation (The Library of Phi)

An initiative to democratize access to high-quality textbooks by employing AI techniques to craft factually accurate books.

#### Generating Textbooks

1. **Dry Run:**

   ```bash
   python sciphi/scripts/generate_textbook.py dry_run
   ```

2. **Default Textbook Generation:**

   ```bash
   python sciphi/scripts/generate_textbook.py run --textbook=Aerodynamics_of_Viscous_Fluids --rag-enabled=False --filter_existing_books=False --log-level=debug
   ```

   [Sample Output](sciphi/data/library_of_phi/sample/Aerodynamics_of_Viscous_Fluids.md)

3. **Using Custom Table of Contents:** 

   Draft and save as `textbook_name.yaml`, then place it in the specified directory.

4. **Incorporating RAG:** 

   Set rag-enabled=True and set the appropriate `.env` variables, or pass in values for `rag_api_base` and `rag_api_key`.

_Note:_ Ensure alignment with our specifications if using Wikipedia for RAG. Explore more examples [here](https://github.com/emrgnt-cmplxty/library_of_phi/tree/main).


### RAG Eval Harness

We introduce a RAG evaluation harness in order to evaluate the performance of a given RAG pipeline.

#### RAG Harness

1. **Run the Harness:**

   ```bash
   poetry run python sciphi/scripts/rag_harness.py --n-samples=100 --rag-enabled=True --evals_to_run="science_multiple_choice"
   ...
   INFO:__main__:Final Accuracy=0.65
   ```


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

## Citations & References

- [Textbooks Are All You Need](https://arxiv.org/abs/2306.11644)
- [Textbooks Are All You Need II: Phi-1.5 Technical Report](https://arxiv.org/abs/2309.05463)

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

---

Note: This version assumes you have a `requirements.txt` file that lists all the necessary dependencies for `pip` to install. If such a file doesn't exist, you'll need to create one.
