# SciPhi: A framework for breaking scaling laws

## Overview

SciPhi is a Python package that provides two high-level features:

Configurable generation of synthetic and instruction fine-tuning data for LLMs.
A framework for LLM based evaluation of the output from other LLMs.

## Installation

```bash
# Repository setup
git clone https://github.com/emrgnt-cmplxty/sciphi.git
cd sciphi
# Install dependencies
poetry sciphi -E openai_support
# Add other optional dependencies
# poetry install -E openai_support -E anthropic_support -E hf_support, ...
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

## Usage

### Dataset Generation

You can use SciPhi for dataset generation by executing the relevant `runner.py` file with various command-line arguments.

```bash
poetry run python sciphi/examples/data_generation/runner.py --provider_name=openai --model_name=gpt-4 --log_level=DEBUG --batch_size=1 --num_samples=1 --output_file_name=example_output.jsonl
```

### Key Command-Line Arguments

- `--provider`: Which provider to use for completions (default: "openai").
- `--model_name`: The name of the model to load from the provider (default: "gpt-3.5-turbo").
- `--temperature`: Temperature parameter for the provided model (default: 0.7).
- `--example_config`: Which example configuration to use (default: "python_textbook").
- `--num_samples`: Number of samples to generate (default: 1_024).
- `--output_dir`: File path to override the default output output file path with.
- `--output_file_name`: Filename to override the default output file name with.

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
data_maker = DataMaker()
data_maker.load_config_from_yaml(
    args.config_path
    or os.path.join(get_data_config_dir(), f"{args.example_config}.yaml")
)

...
writer = JsonlDataWriter(output_path)

# Generate the data and write the results
for entry in data_maker.generator(args.num_samples):
    batch = []
    for entry in data_maker.generator(args.num_samples):
        batch.append(entry)

        if len(batch) == args.batch_size:
            for it in range(len(completions)):
                formatted_prompt = batch[it]["formatted_prompt"]
                # Write the results using DataWriter
                writer.write(
                    [
                        {
                            "formatted_prompt": formatted_prompt,
                            "completion": llm_provider.get_completion(formatted_prompt),
                        }
                    ]
                )

        batch = []
```

### License

This project is licensed under the Apache-2.0 License.

### Sources

[1] [GPT-4 Technical Report](https://arxiv.org/abs/2303.08774)

[2] [Sparks of Artificial General Intelligence](https://arxiv.org/pdf/2303.12712.pdf)

[3] [Solving Challenging Math Word Problems Using GPT-4 Code Interpreter with Code-based Self-Verification](https://paperswithcode.com/paper/solving-challenging-math-word-problems-using)