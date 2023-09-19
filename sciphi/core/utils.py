"""A module which defines utilities for the library."""
import json
import logging
import os

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
    return os.path.join(script_dir, "..", "data", "stock_config")
