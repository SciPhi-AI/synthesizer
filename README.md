# SciPhi: A framework for breaking scaling laws

## Overview

The SciPhi Framework is designed as simply as possible to facilitate the generation of synthetic or fine-tuning data. Additionally, it facilitates LLM-based evaluation of LLM output.

## Installation

```bash
# Repository setup
git clone https://github.com/emrgnt-cmplxty/sciphi.git
cd sciphi
# Install dependencies
poetry sciphi -E openai_support
# Add other optional dependencies
# poetry install -E anthropic_support,openai_support, ...
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
poetry run python sci_phi/examples/data_generation/runner.py --provider_name=openai --model_name=gpt-4 --log_level=DEBUG
```

### Key Command-Line Arguments

- `--provider`: Which provider to use for completions (default: "openai").
- `--model_name`: The name of the model to load from the provider (default: "gpt-3.5-turbo").
- `--temperature`: Temperature parameter for the provided model (default: 0.7).
- `--output_file_name`: Filename to override the default output file name with.

## License

This project is licensed under the Apache-2.0 License.

## Sources

[1] [GPT-4 Technical Report](https://arxiv.org/abs/2303.08774)

[2] [Sparks of Artificial General Intelligence](https://arxiv.org/pdf/2303.12712.pdf)

[3] [Solving Challenging Math Word Problems Using GPT-4 Code Interpreter with Code-based Self-Verification](https://paperswithcode.com/paper/solving-challenging-math-word-problems-using)