import argparse
import json
import logging
import os
from typing import Optional

import pandas as pd


def load_file_or_raise(path: str) -> pd.DataFrame:
    """Utility function to load a file or raise an error if not found."""

    try:
        file_extension = os.path.splitext(path)[-1].lower()
        if file_extension == ".csv":
            return pd.read_csv(path)
        elif file_extension == ".jsonl":
            with open(path, "r", encoding="utf-8") as file:
                return pd.DataFrame(
                    json.loads(line) for line in file if line.strip()
                )
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Please check the expected data at {path}."
        ) from e


def load_existing_jsonl(file_path: str) -> list[dict]:
    """Load existing results from a jsonl file."""
    if os.path.exists(file_path):
        with open(file_path, "r") as json_file:
            return [json.loads(line) for line in json_file]
    return []


def get_configured_logger(name: str, log_level: str) -> logging.Logger:
    """Get a configured logger."""
    log_level = getattr(logging, log_level.upper(), "INFO")
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(name)


def get_root_dir() -> str:
    """Get the path to the root of the code repository."""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(script_dir, "..", "..")


def get_data_config_dir() -> str:
    """Get the path to the root of the code repository."""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(script_dir, "..", "data_config")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(
        description="Parse Sci-Phi running commands"
    )
    # Run arguments
    parser.add_argument(
        "--run_name",
        type=str,
        default="run_0",
        help="The name of the run.",
    )
    parser.add_argument(
        "--provider_name",
        type=str,
        default="openai",
        help="Which provider to use for zero-shot completions?",
    )
    # Base LLM arguments
    parser.add_argument(
        "--model_name",
        type=str,
        default="gpt-3.5-turbo",
        help="Model name to load from the provider.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Temperature parameter for provided model.",
    )
    parser.add_argument(
        "--top_p",
        type=float,
        default=1,
        help="Top-p parameter for provided model.",
    )
    # Model dependent arguments (each defaults to None)
    parser.add_argument(
        "--top_k",
        type=float,
        default=None,
        help="Top-k parameter for provided model.",
    )
    parser.add_argument(
        "--max_tokens_to_sample",
        type=int,
        default=None,
        help="Max tokens to sample for each completion from the provided model.",
    )
    parser.add_argument(
        "--do_sample",
        type=bool,
        default=None,
        help="Should the model run with sampling?",
    )
    parser.add_argument(
        "--num_beams",
        type=int,
        default=None,
        help="The number of beams to use for beam search.",
    )
    parser.add_argument(
        "--do_stream",
        type=bool,
        default=None,
        help="Should the model run with streaming?",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Which device should the model run on (relevant for local models, like HuggingFace)?",
    )
    parser.add_argument(
        "--add_model_kwargs",
        type=dict,
        default=None,
        help="Additional model kwargs for HuggingFace model.",
    )
    parser.add_argument(
        "--add_tokenizer_kwargs",
        type=dict,
        default=None,
        help="Additional tokenizer kwargs for HuggingFace model.",
    )
    parser.add_argument(
        "--add_generation_kwargs",
        type=dict,
        default=None,
        help="Additional generation kwargs for HuggingFace model.",
    )
    parser.add_argument(
        "--functions",
        type=list[dict],
        default=None,
        help="Functions list for OpenAI model.",
    )
    parser.add_argument(
        "--version",
        type=str,
        default="0.1.0",
        help="Version of this run.",
    )
    # Prompt arguments
    parser.add_argument(
        "--prompt_type",
        type=str,
        default="md_instruction",
        help="Which prompt type to use for generation completions?",
    )
    parser.add_argument(
        "--prompt_override",
        type=str,
        default="",
        help="Override the prompt type for the prompt with a comma separated list. The first entry is the prompt, followed by expected prompt inputs. E.g. `my_prompt requires {input},input`",
    )
    # Data generation arguments
    parser.add_argument(
        "--batch_size",
        type=int,
        default=64,
        help="Number of examples to generate per batch.",
    )
    parser.add_argument(
        "--config_path",
        type=Optional[str],
        default=None,
        help="Optional path to the configuration path, if specified the example config is overridden.",
    )
    parser.add_argument(
        "--example_config",
        type=str,
        default="python_textbook",
        help="Which configuration to use for data generation?",
    )
    parser.add_argument(
        "--extra_output_file_text",
        default="",
        help="Extra text to append to the end of the string.",
    )
    parser.add_argument(
        "--log_level",
        type=str,
        default="INFO",
        help="Logging verbosity level.",
    )
    parser.add_argument(
        "--num_samples",
        type=int,
        default=1_024,
        help="Number of samples to generate.",
    )
    parser.add_argument(
        "--output_file_name",
        default=None,
        help="Filename to override the default output file name with.",
    )
    parser.add_argument(
        "--output_dir",
        default="outputs",
        help="Directory to write generated output to.",
    )
    return parser.parse_args()


def prep_for_file_path(in_path: str) -> str:
    """Prepare a string to be used in a file path."""
    return in_path.replace("-", "_").replace(".", "p").replace("/", "_")
