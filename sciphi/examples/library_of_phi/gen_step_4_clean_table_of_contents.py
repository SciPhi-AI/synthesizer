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
    
    num_processes (int):
        Number of processes to use. Defaults to the number of CPUs available.
"""

import logging
import os
import pathlib
from concurrent.futures import ThreadPoolExecutor
from glob import glob

import fire
import yaml

from sciphi.examples.helpers import (
    get_default_settings_provider,
    traverse_config,
    with_retry,
)
from sciphi.examples.library_of_phi.prompts import (
    TABLE_OF_CONTENTS_CLEAN_PROMPT,
)


def ensure_directory_exists(directory_path: str):
    """Ensure that the directory exists. If not, create it."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def get_field_and_subfield_from_filename(filename: str) -> tuple:
    """Extract field and subfield from the given filename."""
    field = filename.split("_subfield_")[0][6:]
    subfield = filename.split("subfield_")[1].split("_course_name")[0]
    return field, subfield


# Utility function to construct the config from text
def construct_config(text: str) -> dict:
    lines = text.strip().split("\n")

    # Initial structure
    toc = {}
    current_chapter = None
    current_section = None

    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped.startswith("textbook:"):
            textbook_title = lines[i + 1].strip().strip('"')
            toc["textbook"] = {textbook_title: {"chapters": []}}
        elif stripped.startswith("- Chapter"):
            current_chapter = {stripped.strip(): {"sections": []}}
            toc["textbook"][textbook_title]["chapters"].append(current_chapter)
        elif stripped.startswith("- Section:"):
            current_section = {stripped.strip(): {"subsections": []}}
            if current_chapter:
                current_chapter_key = list(current_chapter.keys())[0]
                current_chapter[current_chapter_key]["sections"].append(
                    current_section
                )
        elif stripped.startswith("- ") and current_section:
            current_section_key = list(current_section.keys())[0]
            current_section[current_section_key]["subsections"].append(
                stripped[2:].strip()
            )
    return toc


class CleanTableOfContentsRunner:
    """Class to run the cleaning of detailed Table of Contents."""

    def __init__(
        self,
        provider: str = "openai",
        model_name: str = "gpt-3.5-turbo-16k-0613",
        data_directory=None,
        input_rel_dir: str = "output_step_3",
        output_rel_dir: str = "output_step_4",
        log_level: str = "INFO",
        num_processes: int = None,
    ):
        self.input_rel_dir = input_rel_dir
        self.output_rel_dir = output_rel_dir
        self.data_directory = data_directory
        self.provider = provider
        self.model_name = model_name
        # Build an LLM and provider interface
        self.llm_provider = get_default_settings_provider(
            provider=self.provider, model_name=self.model_name
        )

        logging.basicConfig(level=getattr(logging, log_level.upper()))
        self.num_processes = num_processes or os.cpu_count()
        logging.info("Running with {self.num_processes} processes")

        # Default data directory to the directory of this script combined with 'raw_data'.
        if not self.data_directory:
            self.data_directory = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "raw_data"
            )

        self.input_dir = os.path.join(self.data_directory, self.input_rel_dir)
        self.output_dir = os.path.join(
            self.data_directory, self.output_rel_dir
        )

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def save_config_to_file(self, yml_config, yml_file_path):
        """Save the YAML config to the appropriate directory structure."""
        name = os.path.basename(yml_file_path)
        field, subfield = get_field_and_subfield_from_filename(name)

        field_dir = os.path.join(self.output_dir, field)
        subfield_dir = os.path.join(field_dir, subfield)

        ensure_directory_exists(field_dir)
        ensure_directory_exists(subfield_dir)

        output_filepath = os.path.join(subfield_dir, name)
        logging.info(f"Saving config to {output_filepath}")
        if os.path.exists(output_filepath):
            logging.info(f"File {output_filepath} already exists. Skipping...")
            return

        with open(output_filepath, "w") as f:
            yaml.dump(yml_config, f, sort_keys=False)

        logging.info(f"Saved config to {output_filepath}")

    def process_file(self, yml_file_path):
        logging.info(f"Processing file at {yml_file_path}")

        name = os.path.basename(yml_file_path)
        field, subfield = get_field_and_subfield_from_filename(name)

        field_dir = os.path.join(self.output_dir, field)
        subfield_dir = os.path.join(field_dir, subfield)
        output_filepath = os.path.join(subfield_dir, name)

        if os.path.exists(output_filepath):
            logging.info(f"File {output_filepath} already exists. Skipping...")
            return

        # Ensure directories exist
        ensure_directory_exists(field_dir)
        ensure_directory_exists(subfield_dir)

        table_of_contents = pathlib.Path(yml_file_path).read_text()
        prompt = TABLE_OF_CONTENTS_CLEAN_PROMPT.format(
            table_of_contents=table_of_contents
        )
        completion = with_retry(
            lambda: self.llm_provider.get_completion(prompt)
        )

        # Save the raw completion
        with open(output_filepath.replace(".yaml", "_raw.txt"), "w") as f:
            f.write(completion)
        logging.info(f"Completion for {output_filepath} = {completion}")

        try:
            yml_config = construct_config(completion)
            traverse_config(yml_config)
            self.save_config_to_file(yml_config, output_filepath)
        except Exception as e:
            logging.error(
                f"Failed to traverse config at {output_filepath} due to {e}"
            )

    def run(self):
        with ThreadPoolExecutor(max_workers=self.num_processes) as executor:
            list(
                executor.map(
                    self.process_file, glob(f"{self.input_dir}/*.yaml")
                )
            )


if __name__ == "__main__":
    fire.Fire(CleanTableOfContentsRunner)
