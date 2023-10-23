"""A module to facilitate seamless construction of input prompts"""
import os
from dataclasses import dataclass
from typing import Optional

import yaml


@dataclass
class Prompt:
    """A simple abstraction for building input prompts."""

    config: dict

    def __init__(
        self, config: Optional[dict] = None, config_path: Optional[dict] = None
    ) -> None:
        if config and config_path or not config and not config_path:
            raise ValueError(
                "Must provide either a config or a config path, but not both."
            )
        if not os.path.exists(config_path):
            raise ValueError(f"Config path {config_path} does not exist.")
        if config_path:
            with open(config_path, "r") as yaml_file:
                config = yaml.safe_load(yaml_file)
        if "raw_text" not in config:
            raise ValueError("Prompt config must contain a `raw_text` field.")
        if "dataset_supplied_inputs_map" not in config:
            raise ValueError(
                "Prompt config must contain a `dataset_supplied_inputs_map` field."
            )
        if "user_supplied_inputs" not in config:
            raise ValueError(
                "Prompt config must contain a `user_supplied_inputs` field."
            )

        self.user_supplied_inputs = config["user_supplied_inputs"]
        self.dataset_supplied_inputs_map = config[
            "dataset_supplied_inputs_map"
        ]
        self.dataset_expected_inputs = list(
            config["dataset_supplied_inputs_map"].values()
        )
        self.dataset_expected_columns = list(
            config["dataset_supplied_inputs_map"].keys()
        )
        if set(self.user_supplied_inputs).intersection(
            self.dataset_expected_inputs
        ):
            raise ValueError(
                "Prompt config cannot overlap `user_supplied_inputs` and `dataset_supplied_inputs_map` values."
            )
        self.expected_inputs = set(
            self.user_supplied_inputs + self.dataset_expected_inputs
        )
        self.raw_text = config["raw_text"]

    def format(self, dataset_entry: Optional[dict] = None, **kwargs) -> str:
        """Format the prompt into a string"""
        if self.dataset_expected_columns and not dataset_entry:
            raise ValueError(
                "Expected a dataset entry, but none was provided."
            )
        for key in self.dataset_expected_columns:
            if key not in dataset_entry:
                raise ValueError(
                    f"Expected dataset entry to contain {key}, but it was not found."
                )
            kwargs[self.dataset_supplied_inputs_map[key]] = dataset_entry[key]

        if set(kwargs.keys()) != self.expected_inputs:
            raise ValueError(
                f"Received {kwargs.keys()}, but expected {self.expected_inputs}"
            )
        if not isinstance(self.raw_text, str):
            raise ValueError(
                f"Expected `raw_text` to be a string, but got {type(self.raw_text)}"
            )
        return self.raw_text.format(**kwargs)

    @property
    def text(self):
        if not self._text:
            raise ValueError(
                "Format prompt before attempting to access the `text` field."
            )
        return self._text

    # @property
    # def required_data_fields(self):
    #     return self.config["dataset_supplied_inputs"].keys()
