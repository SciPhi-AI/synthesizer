"""A module to manage prompt generation for a given configuration."""
import random
from typing import Union


class PromptGenerator:
    """A class for generating prompts from a data config."""

    RAW_PROMPT_TAG = "raw_prompt"
    FORMATTED_PROMPT_TAG = "formatted_prompt"

    # TODO - Add type restrictions for config
    def __init__(
        self,
        config: dict,
        prompt_templates: dict[str, int],
        prompt_template_input_dependencies: dict[str, str],
        prompt_dataset_dependencies: dict[str, str],
        prompt_inputs: list[str],
    ):
        self.config = config
        self.prompt_templates = prompt_templates
        self.prompt_template_input_dependencies = (
            prompt_template_input_dependencies
        )
        self.prompt_inputs = prompt_inputs
        self.prompt_dataset_dependencies = prompt_dataset_dependencies

    @staticmethod
    def _random_sample(vars_and_weights: dict) -> str:
        """Randomly sample a weighted dictionary."""

        keys, weights = zip(*vars_and_weights.items())
        if len(keys) == 0:
            raise IndexError("Cannot randomly sample an empty input.")
        return random.choices(keys, weights)[0]

    def generate_prompt(self, optional_formatters=None) -> dict:
        """Return a prompt and its inputs."""
        # Build the prompt formatters
        formatters: dict[str, str] = optional_formatters or {}

        # self.prompt_input_dependencies is a dictionary of dictionaries
        # The outer dictionary is keyed by the prompt input
        # The inner dictionary is keyed by the prompt input dependency
        # It can be `None` if there are no dependencies
        for prompt_input in self.prompt_inputs:
            entry = self.config[prompt_input]
            if (
                self.prompt_dataset_dependencies
                and prompt_input in self.prompt_dataset_dependencies
            ):
                # Parse dataset dependencies
                entry = PromptGenerator._random_sample(entry)

                self._insert_formatter(
                    formatters, prompt_input, optional_formatters[entry]
                )
            elif (
                self.prompt_template_input_dependencies
                and prompt_input in self.prompt_template_input_dependencies
            ):
                # Parse single depth dependencies
                dependent_on = self.prompt_template_input_dependencies[
                    prompt_input
                ]
                dependent_value = formatters[dependent_on]
                self._insert_formatter(
                    formatters,
                    prompt_input,
                    entry[dependent_value],
                )
            else:
                self._insert_formatter(formatters, prompt_input, entry)

        prompt = PromptGenerator._random_sample(self.prompt_templates)
        print("prompt=", prompt)
        return {
            PromptGenerator.RAW_PROMPT_TAG: prompt,
            PromptGenerator.FORMATTED_PROMPT_TAG: prompt.format_map(
                formatters
            ),
        }

    @staticmethod
    def _insert_formatter(
        formatters: dict, key: str, entry: Union[dict, str]
    ) -> None:
        """Insert a formatter into the formatters dictionary."""
        if isinstance(entry, dict):
            formatters[key] = PromptGenerator._random_sample(entry)
        elif isinstance(entry, str):
            formatters[key] = entry
        else:
            raise ValueError(
                f"Unexpected type for config entry {key}: {type(entry)}"
            )
