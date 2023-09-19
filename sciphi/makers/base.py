"""A module which facilitates synthesizing prompt data."""
import os
import random
from copy import copy
from enum import Enum
from typing import Dict, Generator, Optional, Union

import yaml

from sciphi.config import DataConfig
from sciphi.prompt import Prompt, PromptGenerator


class DataMaker:
    """A class to facilitate seamless construction of input prompts"""

    class GeneratorMode(Enum):
        """What mode is the data maker in?"""

        SYNTHETIC = "synthetic"
        FROM_HF_DATASET = "from_hf_dataset"

    """A class to synthesize data from a configuration."""

    PROMPT_TEMPLATE_TAG = "prompt_templates"

    def __init__(
        self,
        generator_mode: GeneratorMode,
        prompt_generator: PromptGenerator,
        outer_prompt: Prompt,
        hf_dataset_name: Optional[str] = None,
    ) -> None:
        self.generator_mode = generator_mode
        self.prompt_generator = prompt_generator
        self.outer_prompt = outer_prompt

    def synthetic_generator(
        self, batch_size: int, num_samples: int
    ) -> Generator[Dict[str, str], None, None]:
        """Returns a generator which yields formatted prompts from the loaded configuration."""

        counter = 0
        while counter < num_samples:
            batch = []

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
    ) -> Generator[Dict[str, str], None, None]:
        """Returns a generator which yields formatted prompts from the loaded configuration."""
        raise NotImplementedError("Not yet implemented.")
        # if batch_size != 1:
        #     raise ValueError(
        #         "Batch size must be 1 for HuggingFace dataset generation."
        #     )

        # try:
        #     from datasets import load_dataset
        # except:
        #     raise ImportError(
        #         "Please install the `datasets` package before attempting to run with a HuggingFace dataset generator. This can be accomplished via `poetry install -E hf_support, ...OTHER_DEPENDENCY_HERE`."
        #     )

        # dataset = load_dataset(self.dataset_name, streaming=True)

        # for data in dataset["train"]:
        #     result = {
        #         inner_key: data[
        #             inner_generator[DataMaker.Mode.FROM_HF_DATASET.value]
        #         ]
        #         if [DataMaker.Mode.FROM_HF_DATASET.value]
        #         == list(inner_generator.keys())
        #         else self.random_sample(inner_generator)
        #         for inner_key, inner_generator in self.config.items()
        #     }
        #     self.outer_prompt.format(**result)
        #     if self.outer_prompt.structure != PromptStructure.SINGLE:
        #         raise NotImplementedError(
        #             "Not yet implemented for multi-prompt datasets."
        #         )
        #     result["raw_prompt"] = self.outer_prompt.raw_text
        #     result["formatted_prompt"] = self.outer_prompt.text
        #     yield result
        #     counter += 1
        #     if counter >= num_samples:
        #         break

    def generator(
        self, batch_size=1_024, num_samples=1_048_576
    ) -> Generator[Dict[str, str], None, None]:
        """Returns a generator which yields formatted prompts from the loaded configuration."""

        if self.generator_mode == DataMaker.GeneratorMode.SYNTHETIC:
            yield from self.synthetic_generator(batch_size, num_samples)
        elif self.generator_mode == DataMaker.GeneratorMode.FROM_HF_DATASET:
            yield from self.hf_dataset_generator(batch_size, num_samples)
        else:
            raise ValueError(
                f"Invalid generation mode {self.generator_mode} specified. Must be one of {DataMaker.GeneratorMode}."
            )
