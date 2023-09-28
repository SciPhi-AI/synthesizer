# SciPhi [ΨΦ]: A framework for breaking LLM scaling laws

## Overview

SciPhi is a Python package that provides two high-level features:

- Configurable generation of LLM-mediated synthetic training / tuning data for LLMs.
- Seamless LLM-mediated evaluation of model output.

<p align="center">
<img width="524" alt="Screenshot 2023-09-18 at 9 53 55 AM" src="https://github.com/emrgnt-cmplxty/SciPhi/assets/68796651/9731f891-1d99-432a-aaec-37916bc6362f">
</p>

## Questions?

Join us on [Discord here](https://discord.gg/j9GxfbxqAe) or [contact me](mailto:owen@emergentagi.com) directly. For a SciPhi tutorial, [go here](https://substack.com/inbox/post/137197905).

## Installation

```bash
# Repository setup
git clone https://github.com/emrgnt-cmplxty/sciphi.git
cd sciphi
# Install dependencies
# pip3 install poetry (if you don't have it)
poetry install -E all
# Setup your environment
cp .env.example .env && vim .env
```

---

## Requirements

- Python >= 3.11 and < 3.12
- Poetry for package management

### Optional Feature Requirements

For additional features, you can install the optional dependencies:

```bash
poetry install -E <extra_name>
```

- `anthropic_support`: For running with Anthropic models.
- `hf_support`: For running with the HuggingFace package, useful for a large variety of model access.
- `openai_support`: For running with OpenAI models.
- `vllm_support`: For with VLLM, useful for fast inference.
- `llama_index_support`: For LlamaIndex, useful for grounded synthesis.
- `chroma_support`: For Chroma support, used for large vector databases.
- `all`: For all dependencies (ex-vllm, which requires a separate install).

## Usage

### Dataset Generation

You can use SciPhi for dataset generation by executing the relevant `runner.py` file with various command-line arguments.

```bash
poetry run python sciphi/examples/basic_data_gen/runner.py --provider_name=openai --model_name=gpt-4 --log_level=DEBUG --batch_size=1 --num_samples=1 --output_file_name=example_output.jsonl --example_config=textbooks_are_all_you_need_basic_split
```

### Key Command-Line Arguments

- `--provider`: Which provider to use for completions (default: "openai").
- `--model_name`: The name of the model to load from the provider (default: "gpt-3.5-turbo").
- `--temperature`: Temperature parameter for the provided model (default: 0.7).
- `--example_config`: Which example configuration to use (default: "textbooks_are_all_you_need_basic_split").
- `--override_config_path`: Used to override the example configurations with custom config.
- `--num_samples`: Number of samples to generate (default: 1_024).
- `--output_dir`: File path to override the default output output file path with.
- `--output_file_name`: Filename to override the default output file name with.

### Stock data configs

- `evol_instruct` - A config for replicating the EvolInstruct dataset
- `textbooks_are_all_you_need_basic_split` - A config for replicating the Python textbook data from Textbooks Are All You Need [2]
  
### Example generated data
<img width="776" alt="Screenshot 2023-09-17 at 11 11 18 PM" src="https://github.com/emrgnt-cmplxty/SciPhi/assets/68796651/8f1ef11d-cd37-4fc7-a7a0-a1e0159ba4a3">

## Development


The code snippet below shows how to use SciPhi to generate synthetic data for a given LLM provider.

```python
# Build an LLM and provider interface
llm_config = LLMConfigManager.get_config_for_provider(
    provider_name
).create(**build_llm_config(args))
llm_provider = InterfaceManager.get_provider(
    provider_name,
    model_name,
    llm_config,
)

# Initialize the data maker
data_maker = DataMaker(
    DataGeneratorMode(data_config.generator_mode),
    prompt_generator,
    prompt,
    # Optional field,
    # currently only used when generator_mode == "from_hf_dataset"
    dataset_name=data_config.dataset_name,
)

# Generate & write out the results
output_path = get_output_path(args)
logger.debug(f"Writing results to: {output_path}.")
writer = JsonlDataWriter(output_path)

for batch in data_maker.generator(args.batch_size, args.num_samples):
    completions = llm_provider.get_batch_completion(batch)
    for formatted_prompt, completion in zip(batch, completions):
        logger.debug("-" * 100)
        logger.debug(f"Formatted Prompt:\n{formatted_prompt}")
        logger.debug(f"\nCompletion:\n{completion}")
        logger.debug("-" * 100)

        # Write the results using DataWriter
        writer.write(
            [
                {
                    "formatted_prompt": formatted_prompt,
                    "completion": completion,
                }
            ]
        )

```

### License

This project is licensed under the Apache-2.0 License.

### Datasets Generated

[1] [Python Synthetic Textbooks](https://huggingface.co/datasets/emrgnt-cmplxty/sciphi-python-textbook/viewer/default/train)
[2] [Textbooks are all you need](https://huggingface.co/datasets/emrgnt-cmplxty/sciphi-textbooks-are-all-you-need)

### Sources

[1] [WizardCoder: Empowering Code Large Language Models with Evol-Instruct](https://arxiv.org/abs/2306.08568)

[2] [Textbooks Are All You Need](https://arxiv.org/abs/2306.11644)


## 📖 Citation

Reference to cite if you use LlamaIndex in a paper:

```
@software{Emergent_AGI_SciPhi,
author = {Colegrove, Owen},
doi = {Pending},
month = {09},
title = {{LlamaIndex}},
url = {https://github.com/emrgnt-cmplxty/sciphi},
year = {2023}
}
```
