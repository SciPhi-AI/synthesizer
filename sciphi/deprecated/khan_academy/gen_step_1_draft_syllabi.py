# type: ignore
"""
MIT OCW Course Data Scraper to syllyabi 'Draft' YAML Generator

Description:
    This script is designed to scrape course data from the MIT OpenCourseWare (OCW) website and 
    generate input YAML files with the help of an LLM.

Usage:
    Command-line interface:
        $ python sciphi/library_of_phi/gen_step_1_draft_syllabi.py run \
            --output_rel_dir=my_output_directory \
            --input_jsonl_filename=my_input_file.jsonl \
            --log_level=DEBUG
Parameters:
    
    provider (str):
        The provider to use for LLM completions.
        Default is 'openai'.
    
    model_name (str):
        The model to use for LLM completions.
        Default is 'gpt-4-0613'.

    data_directory (Optional[str]): 
        The directory the input and output data is to be stored.
        If none, defaults to the directory of this script plus '/raw_data'.

    output_rel_dir (str): 
        The relative directory within the data directory where the generated YAML files will be saved. 
        Default value is 'output_step_1'.

    input_jsonl_filename (str): 
        The name of the input jsonl file containing course data scraped from MIT OCW.
        Default value is 'output_step_1'.

    log_level (str): 
        Logging level for the scraper. Can be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL. 
        Default is 'INFO'.
"""

import json
import logging
import os
import re
from glob import glob
from typing import Optional, Set

import fire
import yaml

from sciphi.examples.khan_academy.prompts import SYLLABI_CREATION_PROMPT
from sciphi.textbook_generation.helpers import (
    get_default_settings_provider,
    prase_yaml_completion,
    save_yaml,
)


def extract_data_from_record(record: dict[str, str]) -> tuple[dict, str]:
    """Extract and organize data from a given record."""
    context = f"### Course Name:\n{record['course_title'].replace(':', '')}\n"
    topics = {}
    page_contents = record["page_contents"]["syllabus"]

    for topic in page_contents["topics"]:
        context += f"## Page:\n{topic}\n"
        topics[topic] = "\n".join(page_contents["topics"][topic])

        table = "\n".join(page_contents["topics"][topic])
        context += f"Information:\n{table}\n"

    return topics, context


def get_mapped_topics(topics: str) -> dict[str, str]:
    """Get mapped topics based on depth."""
    mapped_topics = {}
    for topic in topics:
        if topics[topic] == 0:
            mapped_topics["category"] = topic
        elif topics[topic] == 1:
            mapped_topics["field"] = topic
        elif topics[topic] == 2:
            mapped_topics["subfield"] = topic
            break
    return mapped_topics


def get_observed_files(output_dir: str) -> Set[str]:
    """Get set of previously observed files."""
    observed_files = set([])
    for yaml_file in glob(f"{output_dir}/**/*.yaml"):
        with open(yaml_file, "r") as existing_file:
            yaml_load = yaml.safe_load(existing_file)
            if "course" in yaml_load:
                for course_name in yaml_load["course"]:
                    _, discipline, field = yaml_file.split("/")
                    field = field.replace(".yaml", "")
                    subfield = yaml_load["course"][course_name]["subfield"]
                    observed_files.add(
                        f"field_{field}_subfield_{subfield}_course_name_{course_name.replace(' ','_')}"
                    )
    for yaml_dumps in glob(f"{output_dir}/*.yaml"):
        observed_files.add(yaml_dumps.split("/")[-1].replace(".yaml", ""))
    return observed_files


def quoted_presenter(dumper, data):
    """Define a custom representer for string scalars that applies quotes."""
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')


class DraftSyllabiYAMLRunner:
    """Runs the generation process for draft syllabi YAMLs."""

    def __init__(
        self,
        provider: str = "openai",
        model_name: str = "gpt-4-0613",
        data_directory: Optional[str] = None,
        output_rel_dir: str = "output_step_1",
        input_jsonl_filename: str = "ka_scraped.jsonl",
        prompt: str = SYLLABI_CREATION_PROMPT,
        log_level: str = "INFO",
    ):
        self.provider = provider
        self.model_name = model_name
        self.data_directory = data_directory
        self.output_rel_dir = output_rel_dir
        self.input_jsonl_filename = input_jsonl_filename
        self.prompt = prompt
        logging.basicConfig(level=getattr(logging, log_level.upper()))

    def run(self) -> None:
        """Run the draft YAML generation process."""
        yaml.add_representer(str, quoted_presenter)

        llm_provider = get_default_settings_provider(
            provider=self.provider, model_name=self.model_name
        )
        if not self.data_directory:
            file_path = os.path.dirname(os.path.abspath(__file__))
            self.data_directory = os.path.join(file_path, "raw_data")

        output_dir = os.path.join(self.data_directory, self.output_rel_dir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        logging.info(f"Saving data to output directory = {output_dir}")

        # The input file path = data directory + input file name
        input_file_path = os.path.join(
            self.data_directory, self.input_jsonl_filename
        )

        with open(input_file_path, "r") as file:
            for line in file:
                try:
                    record = json.loads(line)

                    # Don't use the topics in KA, and all the context is in the string
                    _, context = extract_data_from_record(record)

                    course_name = record["course_title"]

                    # Replace all non-alphanumeric characters with underscores
                    dump_name = re.sub(
                        r"\W+", "", course_name.replace(" ", "_")
                    )

                    if os.path.exists(
                        os.path.join(output_dir, f"{dump_name}.yaml")
                    ):
                        logging.warn(
                            f"Skipping {dump_name} because it was already created..."
                        )
                        continue

                    formatted_prompt = self.prompt.format(
                        course_name=course_name,
                        context=context,
                    )

                    completion = llm_provider.get_completion(formatted_prompt)

                    data_to_save = {
                        "completion": completion,
                        "course_name": course_name,
                    }

                    yaml_completion = prase_yaml_completion(data_to_save)
                    yml_load = yaml.safe_load(yaml_completion)
                    save_yaml(
                        yml_load,
                        os.path.join(output_dir, f"{dump_name}.yaml"),
                    )

                except Exception as e:
                    logging.error(
                        f"Failed to create output yaml at {self.data_directory} with error: {e}"
                    )


if __name__ == "__main__":
    fire.Fire(DraftSyllabiYAMLRunner)
