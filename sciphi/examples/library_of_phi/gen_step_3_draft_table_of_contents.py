# type: ignore
"""
YAML Syllabi to YAML 'Draft' Table of Contents Generator

Description:
    This script processes YAML files and generates a detailed Table of Contents for a new textbook accompanying the course.

Usage:
    Command-line interface example:
        $ python sciphi/examples/library_of_phi/gen_step_3_draft_table_of_contents.py run \
            --input_dir=output_step_3 \
            --provider=openai \
            --model_name=gpt-4-0613 \
            --log_level=DEBUG
Parameters:
    provider (str): 
        The provider to use for LLM.
        Default is 'openai'.
    
    model_name (str): 
        The model to use for LLM.
        Default is 'gpt-4-0613'.

    data_directory (Optional[str]): 
        The directory input / output data is stored.
        If none, defaults to the directory of this script plus '/raw_data'.

    input_rel_dir (str): 
        The folder for the input JSONL files containing the first pass YAML data. 
        Defaults to 'output_step_1'.

    output_rel_dir (str): 
        The directory where the parsed YAML files will be saved. 
        Defaults to 'output_step_2'.

    log_level (str): 
        Logging level for the scraper. Can be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL. 
        Default is 'INFO'.
"""

import logging
import os
from glob import glob

import fire

from sciphi.examples.helpers import get_default_settings_provider
from sciphi.examples.library_of_phi.prompts import (
    TABLE_OF_CONTENTS_DRAFT_PROMPT,
)


class DraftTableOfContentsRunner:
    """Class to run the generation of detailed 'draft' Table of Contents for textbooks based on YAML syllabus."""

    def __init__(
        self,
        provider: str = "openai",
        model_name: str = "gpt-4-0613",
        input_rel_dir: str = "output_step_2",
        output_rel_dir: str = "output_step_3",
        data_directory=None,
        log_level: str = "INFO",
    ):
        self.provider = provider
        self.model_name = model_name
        self.input_rel_dir = input_rel_dir
        self.output_rel_dir = output_rel_dir
        self.data_directory = data_directory
        logging.basicConfig(level=getattr(logging, log_level.upper()))

    def run(self):
        """Main function."""

        # Default data directory to the directory of this script combined with 'raw_data'.
        if not self.data_directory:
            self.data_directory = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "raw_data"
            )

        # Build an LLM and provider interface
        llm_provider = get_default_settings_provider(
            provider=self.provider, model_name=self.model_name
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
                formatted_prompt = TABLE_OF_CONTENTS_DRAFT_PROMPT.format(
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
    fire.Fire(DraftTableOfContentsRunner)
