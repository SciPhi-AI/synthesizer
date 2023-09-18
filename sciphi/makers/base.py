"""A module which facilitates synthesizing prompt data."""
import os
import random
from enum import Enum
from typing import Dict, Generator, Optional, Union

import yaml

from sciphi.prompt import PromptManager, PromptStructure


class DataMaker:
    """A class to facilitate seamless construction of input prompts"""

    class Mode(Enum):
        """What mode is the data maker in?"""

        SYNTHETIC = "synthetic"
        FROM_HF_DATASET = "from_hf_dataset"

    """A class to synthesize data from a configuration."""

    PROMPT_TEMPLATE_TAG = "prompt_templates"

    def __init__(self):
        self.config: Dict[str, Union[str, Dict[str, str]]] = {}
        self.mode: Optional[DataMaker.Mode] = None
        self.dataset_name: Optional[str] = None

    def load_config_from_dict(
        self, config: Dict[str, Union[str, Dict[str, str]]]
    ):
        """Load configuration from a dictionary."""

        self.config = config
        self.generation_mode = DataMaker.Mode(
            config.pop("generation_mode", DataMaker.Mode.SYNTHETIC.value)
        )
        self._set_mode_from_config(self.config)

    def load_config_from_yaml(self, yaml_path: str) -> None:
        """Load configuration from a YAML file."""

        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"YAML file not found at {yaml_path}")

        with open(yaml_path, "r") as file:
            self.config = yaml.safe_load(file)
        self._set_mode_from_config(self.config)

    def synthetic_generator(
        self, batch_size: int, num_samples: int
    ) -> Generator[Dict[str, str], None, None]:
        """Returns a generator which yields formatted prompts from the loaded configuration."""

        if not self.config:
            raise ValueError(
                "Configuration not loaded. Please load a configuration before synthesizing."
            )

        results = []
        prompt_templates = {
            k: self.config[k].pop(DataMaker.PROMPT_TEMPLATE_TAG)
            for k in self.config
        }
        counter = 0
        while len(results) < batch_size:
            result = {}
            for inner_key, inner_generator in self.config.items():
                inner_prompt = {
                    "text": self.random_sample(prompt_templates[inner_key]),
                    "expected_inputs": set(inner_generator.keys()),
                }

                generated_inputs = {
                    k: self.random_sample(v)
                    for k, v in inner_generator.items()
                }

                formatted_inner = inner_prompt["text"].format(
                    **generated_inputs
                )
                result[inner_key] = formatted_inner

            self.outer_prompt.format(**result)

            if self.outer_prompt.structure == PromptStructure.SINGLE:
                result["raw_prompt"] = self.outer_prompt.raw_text
                result["formatted_prompt"] = self.outer_prompt.text
            else:
                result["raw_prompts"] = [
                    f"[START_PROMPT]{prompt}[END_PROMPT]"
                    for prompt in self.outer_prompt.text
                ]
                result["formatted_prompts"] = [
                    f"[START_PROMPT]{prompt}[END_PROMPT]"
                    for prompt in self.outer_prompt.format(**result).text
                ]
            yield result
            counter += 1
            if counter >= num_samples:
                break

    def hf_dataset_generator(
        self,
        batch_size: int,
        num_samples: int,
    ) -> Generator[Dict[str, str], None, None]:
        """Returns a generator which yields formatted prompts from the loaded configuration."""

        try:
            from datasets import load_dataset
        except:
            raise ImportError(
                "Please install the `datasets` package before attempting to run with a HuggingFace dataset generator. This can be accomplished via `poetry install -E hf_support, ...OTHER_DEPENDENCY_HERE`."
            )

        dataset = load_dataset(self.dataset_name, streaming=True)

        for data in dataset["train"]:
            result = {}

            for inner_key, inner_generator in self.config.items():
                if [DataMaker.Mode.FROM_HF_DATASET.value] == list(
                    inner_generator.keys()
                ):
                    format_key = inner_generator[
                        DataMaker.Mode.FROM_HF_DATASET.value
                    ]
                    result[inner_key] = data[format_key]
                else:
                    result[inner_key] = self.random_sample(inner_generator)
            self.outer_prompt.format(**result)
            if self.outer_prompt.structure == PromptStructure.SINGLE:
                result["raw_prompt"] = self.outer_prompt.raw_text
                result["formatted_prompt"] = self.outer_prompt.text
            else:
                raise NotImplementedError(
                    "Not yet implemented for multi-prompt datasets."
                )
            yield result
            counter += 1
            if counter >= num_samples:
                break

    def generator(
        self, batch_size=1_024, num_samples=1_048_576
    ) -> Generator[Dict[str, str], None, None]:
        """Returns a generator which yields formatted prompts from the loaded configuration."""

        if self.mode == DataMaker.Mode.SYNTHETIC:
            yield from self.synthetic_generator(batch_size, num_samples)
        elif self.mode == DataMaker.Mode.FROM_HF_DATASET:
            yield from self.hf_dataset_generator(batch_size, num_samples)
        else:
            raise ValueError(
                f"Invalid generation mode {self.mode} specified. Must be one of {DataMaker.Mode}."
            )

    @staticmethod
    def random_sample(vars_and_weights: dict) -> str:
        """Randomly sample a weighted dictionary."""

        keys, weights = zip(*vars_and_weights.items())
        if len(keys) == 0:
            raise IndexError("Cannot randomly sample an empty input.")
        return random.choices(keys, weights)[0]

    def _set_mode_from_config(self, config: dict) -> None:
        """Set the generation mode from the configuration."""

        if "generator_mode" not in config:
            raise ValueError("Generator mode not specified in config.")
        if "prompt_mode" not in config:
            raise ValueError("Prompt mode not specified in config.")

        generator_mode = config.pop("generator_mode")
        if isinstance(generator_mode, str):
            self.mode = DataMaker.Mode(generator_mode)
        elif isinstance(generator_mode, dict):
            if [DataMaker.Mode.FROM_HF_DATASET.value] == list(
                generator_mode.keys()
            ):
                self.mode = DataMaker.Mode.FROM_HF_DATASET
                self.dataset_name = generator_mode["from_hf_dataset"]

        prompt_mode = config.pop("prompt_mode")
        self.outer_prompt = PromptManager.get_prompt(prompt_mode)
