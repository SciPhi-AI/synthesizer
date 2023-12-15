"""A module which defines utilities for the library."""
import json
import os
import time
from functools import wraps


def load_existing_jsonl(file_path: str) -> list[dict]:
    """Load existing results from a jsonl file."""
    if os.path.exists(file_path):
        with open(file_path, "r") as json_file:
            return [json.loads(line) for line in json_file]
    return []


def get_root_dir() -> str:
    """Get the path to the root of the code repository."""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(script_dir, "..", "..")


def get_data_dir() -> str:
    """Get the path to the root of the config directory."""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(script_dir, "..", "data")


def get_config_dir() -> str:
    """Get the path to the root of the config directory."""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(script_dir, "..", "config")


class SynthesizerConfig:
    """Configuration class for Synthesizer."""

    def __init__(self, dictionary):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                value = SynthesizerConfig(
                    value
                )  # Recursively convert nested dictionaries
            else:
                value = self._cast_to_appropriate_type(
                    value
                )  # Cast value to its appropriate type
            setattr(self, key, value)

    @staticmethod
    def _cast_to_appropriate_type(value):
        """Automatically cast a value to its appropriate type."""
        # If value is a string representation of an integer
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return value

    def _update_from_dict(self, dictionary):
        """Update fields using a dictionary."""
        for key, value in dictionary.items():
            if isinstance(value, dict):
                existing_value = getattr(self, key, None)
                if existing_value and isinstance(
                    existing_value, SynthesizerConfig
                ):
                    existing_value.update(value)
                else:
                    setattr(self, key, SynthesizerConfig(value))
            else:
                setattr(
                    self, key, self._cast_to_appropriate_type(value)
                )  # Cast value to its appropriate type

    def add_field(self, key, value):
        """Add a field to the configuration."""
        setattr(self, key, value)

    def update(self, new_config_dict):
        """Update fields using a dictionary."""
        self._update_from_dict(new_config_dict)


# Utility to time a function's execution
def time_function(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        return result, elapsed_time

    return wrapper
