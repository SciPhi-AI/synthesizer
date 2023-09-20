"""A module to check that all stock configurations perform as expected."""
import os

from sciphi.config import DataConfig
from sciphi.prompt import PromptGenerator, PromptManager
from sciphi.core.utils import (
    get_data_config_dir,
)

NUM_SAMPLES = 1_000_000
if __name__ == "__main__":
    data_config = DataConfig(
        os.path.join(
            get_data_config_dir(), "textbooks_are_all_you_need/main.yaml"
        )
    )
    prompt_generator = PromptGenerator(
        data_config.config,
        data_config.prompt_templates,
        data_config.prompt_template_input_dependencies,
        data_config.prompt_dataset_dependencies,
        data_config.prompt_inputs,
    )
    for i in range(NUM_SAMPLES):
        prompt_generator.generate_prompt()
