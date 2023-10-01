"""
YAML Syllabi to YAML Table of Contents Generator

Description:
    This script processes YAML files and generates a detailed Table of Contents for a new textbook accompanying the course.

Usage:
    Command-line interface:
        $ python sciphi/examples/library_of_phi/gen_step_3_table_of_contents.py run \
            --input_dir=output_step_2 \
            --provider=openai \
            --model_name=gpt-4-0613 \
            --log_level=DEBUG
Parameters:
    input_dir (str): 
        The directory where the input YAML files are located. 
        Default is 'output_step_2'.
    
    provider (str): 
        The provider to use for LLM.
        Default is 'openai'.
    
    model_name (str): 
        The model to use for LLM.
        Default is 'gpt-4-0613'.

    log_level (str): 
        Logging level for the scraper. Can be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL. 
        Default is 'INFO'.
"""

import logging
import os
from glob import glob

import fire

from sciphi.examples.library_of_phi.prompts import TABLE_OF_CONTENTS_PROMPT  # type: ignore
from sciphi.interface import InterfaceManager, ProviderName
from sciphi.llm import LLMConfigManager


class TableOfContentsRunner:
    """Class to run the generation of detailed Table of Contents for textbooks based on YAML syllabus."""

    def __init__(
        self,
        input_rel_dir: str = "output_step_2",
        output_rel_dir: str = "table_of_contents",
        data_directory=None,
        provider: str = "openai",
        model_name: str = "gpt-4-0613",
        log_level: str = "INFO",
    ):
        self.input_rel_dir = input_rel_dir
        self.output_rel_dir = output_rel_dir
        self.data_directory = data_directory
        self.provider = provider
        self.model_name = model_name
        logging.basicConfig(level=getattr(logging, log_level.upper()))

    def run(self):
        """Main function."""

        # Default data directory to the directory of this script combined with 'raw_data'.
        if not self.data_directory:
            self.data_directory = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "raw_data"
            )

        # Build an LLM and provider interface
        provider_name = ProviderName(self.provider)
        llm_config = LLMConfigManager.get_config_for_provider(
            provider_name
        ).create(max_tokens_to_sample=None)
        llm_provider = InterfaceManager.get_provider(
            provider_name, self.model_name, llm_config
        )

        input_dir = os.path.join(self.data_directory, self.input_rel_dir)
        output_dir = os.path.join(self.data_directory, self.output_rel_dir)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for yml_file_path in glob(f"{input_dir}/*.yaml"):
            try:
                # get end of name
                yml_file_name = os.path.basename(yml_file_path)
                yml_output_file = os.path.join(output_dir, yml_file_name)
                if os.path.exists(yml_output_file):
                    logging.info(
                        f"Skipping {yml_output_file} because it was already created..."
                    )
                    continue
                logging.info(f"Processing YAML file {yml_file_name}...")

                with open(yml_file_path, "r") as yfile:
                    yml_load = yfile.read()
                    course_name = " ".join(
                        yml_file_name.split("name_")[1].split("-")
                    )
                formatted_prompt = TABLE_OF_CONTENTS_PROMPT.format(
                    course_name=course_name, context=yml_load
                )
                logging.debug(
                    f"Passing formatted prompt to LLM: {formatted_prompt}"
                )
                completion = llm_provider.get_completion(formatted_prompt)
                logging.debug(f"Completion: {completion}")
                with open(yml_output_file, "w") as yfile:
                    yfile.write(completion)
            except Exception as e:
                logging.error(
                    f"Failed to process file {yml_file_name} with error {e}."
                )
                pass


if __name__ == "__main__":
    fire.Fire(TableOfContentsRunner)
