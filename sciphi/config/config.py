import os
from typing import Optional

import yaml

from sciphi.config.base import DataGeneratorMode


class DataConfig:
    """Reads the `main` YAML config file and constructs a data config."""

    def __init__(
        self,
        main_config_path: str,
        generator_mode_field: str = "generator_mode",
        prompt_templates_field: str = "prompt_templates",
        prompt_inputs_field: str = "prompt_template_inputs",
        prompt_template_input_dependencies_field: str = "prompt_template_input_dependencies",
        outer_prompt_format_field: str = "outer_prompt_format",
        downstream_configs_field: str = "config_files",
        dataset_name_field: str = "dataset_name",
        prompt_dataset_dependencies_field: str = "prompt_dataset_dependencies",
    ):
        with open(main_config_path, "r") as file:
            self.config = yaml.safe_load(file)
        self.main_path = os.path.dirname(main_config_path)
        self.generator_mode: str = self.config.pop(generator_mode_field)

        # Unpack the prompt config
        self.prompt_templates: dict[str, int] = self.config.pop(
            prompt_templates_field
        )
        self.prompt_inputs: list[str] = self.config.pop(prompt_inputs_field)
        self.prompt_template_input_dependencies: dict[
            str, str
        ] = self.config.pop(prompt_template_input_dependencies_field)
        self.outer_prompt_format: str = self.config.pop(
            outer_prompt_format_field
        )
        self.downstream_configs: dict[str, str] = self.config.pop(
            downstream_configs_field
        )
        self.prompt_dataset_dependencies: dict[str, str] = self.config.pop(
            prompt_dataset_dependencies_field, {}
        )
        self.dataset_name: Optional[str] = self.config.pop(
            dataset_name_field, None
        )

        if (
            self.generator_mode == DataGeneratorMode.FROM_HF_DATASET
            and not self.prompt_dataset_dependencies
        ):
            raise ValueError(
                f"Must specify a dataset name when using {self.generator_mode}."
            )

        self._load_configs()

        # TODO - Add smart config validation
        # self._validate_config()

    def _load_configs(self) -> None:
        """Load the sub-configs into the main config."""

        if not self.downstream_configs:
            return

        for sub_config_name, weight in self.downstream_configs.items():
            with open(
                os.path.join(self.main_path, f"{sub_config_name}.yaml"), "r"
            ) as sub_config_file:
                sub_config = yaml.safe_load(sub_config_file)
                # Merge the sub_config into the main config
                for key in sub_config.keys():
                    entry = sub_config[key]

                    # Unroll dependencies (only single layers are supported now)
                    if key in self.prompt_template_input_dependencies:
                        entry = entry[
                            self.prompt_template_input_dependencies[key]
                        ]

                    if key in self.config and isinstance(entry, dict):
                        # Verify that the sub_config does not overlap with the main config
                        intersection = set(entry.keys()).intersection(
                            set(self.config[key].keys())
                        )
                        if intersection:
                            raise ValueError(
                                f"Sub-config {key} overlaps with main config, resulting in an intersection {intersection}. Note, every key must be unique in the unrolled dictionary."
                            )
                        # Weight the sub_config entries by the weight
                        # If value is a dictionary, then recursively weight the values
                        weighted_entry = {
                            k: v * weight
                            if isinstance(v, int)
                            else {ks: vs * weight for ks, vs in v.items()}
                            for k, v in entry.items()
                        }
                        # Merge the weighted sub_config into the main config
                        self.config[key] = {
                            **weighted_entry,
                            **self.config[key],
                        }
                    elif (
                        key in self.config and isinstance(entry, str)
                    ) or key not in self.config:
                        self.config[key] = entry
                    else:
                        # Only dicts and strings are supported, raise an error otherwise
                        raise ValueError(
                            f"Unexpected type for config entry {key}: {type(entry)}"
                        )
