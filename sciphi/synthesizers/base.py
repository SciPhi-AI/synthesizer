"""A module which facilitates synthesizing prompt data."""
import os
import random
from typing import Dict, Generator, Union

import yaml

from sciphi.prompt import Prompt, PromptStructure


class DataSynthesizer:
    """A class to synthesize data from a configuration."""

    PROMPT_TEMPLATE_TAG = "prompt_templates"

    def __init__(self, outer_prompt: Prompt):
        self.outer_prompt = outer_prompt
        self.config: Dict[str, Union[str, Dict[str, str]]] = {}

    def load_config_from_dict(
        self, config: Dict[str, Union[str, Dict[str, str]]]
    ):
        """Load configuration from a dictionary."""
        self.config = config

    def load_config_from_yaml(self, yaml_path: str) -> None:
        """Load configuration from a YAML file."""
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"YAML file not found at {yaml_path}")

        with open(yaml_path, "r") as file:
            self.config = yaml.safe_load(file)

    def synthesis_generator(
        self, batch_size: int = 1_024
    ) -> Generator[Dict[str, str], None, None]:
        """Returns a generator which yields formatted prompts from the loaded configuration."""
        if not self.config:
            raise ValueError(
                "Configuration not loaded. Please load a configuration before synthesizing."
            )
        results = []
        prompt_templates = {
            k: self.config[k].pop(DataSynthesizer.PROMPT_TEMPLATE_TAG)
            for k in self.config
        }

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

    @staticmethod
    def random_sample(vars_and_weights: dict) -> str:
        """Randomly sample a weighted dictionary."""
        keys, weights = zip(*vars_and_weights.items())
        if len(keys) == 0:
            raise IndexError("Cannot randomly sample an empty input.")
        return random.choices(keys, weights)[0]
