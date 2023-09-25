"""A module which facilitates synthesizing prompt data."""

from copy import copy
from typing import Generator, Optional

from sciphi.config.base import DataGeneratorMode
from sciphi.prompt import Prompt, PromptGenerator


class DataMaker:
    """A class to synthesize data from a configuration."""

    PROMPT_TEMPLATE_TAG = "prompt_templates"

    def __init__(
        self,
        generator_mode: DataGeneratorMode,
        prompt_generator: PromptGenerator,
        outer_prompt: Prompt,
        dataset_name: Optional[str] = None,
        dataset_filters: Optional[dict[str, str]] = None,
    ) -> None:
        self.generator_mode = generator_mode
        self.prompt_generator = prompt_generator
        self.outer_prompt = outer_prompt
        self.dataset_name = dataset_name
        self.dataset_filters = dataset_filters

    def synthetic_generator(
        self, batch_size: int, num_samples: int
    ) -> Generator[list[str], None, None]:
        """Returns a generator which yields formatted prompts from the loaded configuration."""

        counter = 0
        while counter < num_samples:
            batch: list[str] = []

            while len(batch) < batch_size:
                inner_prompt = self.prompt_generator.generate_prompt()
                formatted_outer_prompt = copy(self.outer_prompt)
                formatted_outer_prompt.format(
                    instruction=inner_prompt[
                        PromptGenerator.FORMATTED_PROMPT_TAG
                    ]
                )
                batch.append(formatted_outer_prompt.text)
                counter += 1
            yield batch

    def hf_dataset_generator(
        self,
        batch_size: int,
        num_samples: int,
    ) -> Generator[list[str], None, None]:
        """Returns a generator which yields formatted prompts from the loaded configuration."""
        if batch_size != 1:
            raise ValueError(
                "Batch size must be 1 for HuggingFace dataset generation."
            )

        try:
            from datasets import load_dataset
        except ImportError:
            raise ImportError(
                "Please install the `datasets` package before attempting to run with a HuggingFace dataset generator. This can be accomplished via `poetry install -E hf_support, ...OTHER_DEPENDENCIES_HERE`."
            )

        dataset = load_dataset(self.dataset_name, streaming=True)

        # filter the dataset, on key and list of filter values
        if self.dataset_filters:
            for key, values in self.dataset_filters.items():
                dataset = dataset.filter(
                    lambda example: example[key] in values,
                )
        counter = 0
        for data in dataset["train"]:
            inner_prompt = self.prompt_generator.generate_prompt(
                optional_formatters=data
            )
            formatted_outer_prompt = copy(self.outer_prompt)
            formatted_outer_prompt.format(
                instruction=inner_prompt[PromptGenerator.FORMATTED_PROMPT_TAG]
            )
            yield [formatted_outer_prompt.text]
            counter += 1
            if counter >= num_samples:
                break

    def generator(
        self, batch_size=1_024, num_samples=1_048_576
    ) -> Generator[list[str], None, None]:
        """Returns a generator which yields formatted prompts from the loaded configuration."""

        if self.generator_mode == DataGeneratorMode.SYNTHETIC:
            yield from self.synthetic_generator(batch_size, num_samples)
        elif self.generator_mode == DataGeneratorMode.FROM_HF_DATASET:
            yield from self.hf_dataset_generator(batch_size, num_samples)
        else:
            raise ValueError(
                f"Invalid generation mode {self.generator_mode} specified. Must be one of {DataGeneratorMode}."
            )
