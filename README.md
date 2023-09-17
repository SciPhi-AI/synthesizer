# SciPhi: Train and Evaluate LLMs

## Overview

The SciPhi Framework is designed as simply as possible to facilitate the generation of synthetic or fine-tuning data. Additionally, it facilitates LLM-based evaluation of LLM output.

## Installation

```bash
# Repository setup
git clone https://github.com/emrgnt-cmplxty/sci_phi.git
cd sci_phi
# Install dependencies
poetry install
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

- `anthropoic_support`: For running with Anthropic models.
- `hf_support`: For running with the HuggingFace package, useful for a large variety of model access.
- `openai_support`: For running with OpenAI models.
- `vllm_support`: For with VLLM, useful for fast inference.

## Usage

You can run sciphi replication by executing the `runner.py` file with various command-line arguments.

```bash
poetry run python runner.py --provider openai --dataset human-eval --model gpt-4-0613 --temperature 0.7
```

### Command-Line Arguments

- `--provider`: Which provider to use for zero-shot completions (default: "openai").
- `--dataset`: Which dataset to run on (default: "human-eval").
- `--model`: Model name to load from the provider (default: "gpt-3.5-turbo").
- `--temperature`: Temperature parameter for the provided model (default: 0.7).
- `--output_file_name`: Filename to override the default output file name with.

To see explicit commands ran to generate the reported results, check out the [commands.md](commands.md) menu.

## License

This project is licensed under the Apache-2.0 License.

## Sources

[1] [GPT-4 Technical Report](https://arxiv.org/abs/2303.08774)

[2] [Sparks of Artificial General Intelligence](https://arxiv.org/pdf/2303.12712.pdf)

[3] [Solving Challenging Math Word Problems Using GPT-4 Code Interpreter with Code-based Self-Verification](https://paperswithcode.com/paper/solving-challenging-math-word-problems-using)
# DatasetBuilder
