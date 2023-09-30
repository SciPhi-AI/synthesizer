"""
Syllabi YAML 'draft' to Clean Syllabi YAML Generator

Description:
    This script is designed to scrape course data from the MIT OpenCourseWare (OCW) website and 
    generate YAML files suitable for LLM (Language Learning Model).

Usage:
    Command-line interface:
        $ python sciphi/examples/library_of_phi/gen_step_2_clean_syllabi.py \
            --output_dir=my_output_directory \
            --input_filename=my_input_file.jsonl \
            --log_level=DEBUG
Parameters:
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
import glob
import logging
import os

import fire
import yaml

from sciphi.examples.helpers import load_yaml, prase_yaml_completion, save_yaml


def run(
    data_directory=None,
    input_rel_dir="output_step_1",
    output_rel_dir="output_step_2",
    log_level="INFO",
):
    # Set up logging
    logging.basicConfig(level=log_level.upper())
    logger = logging.getLogger(__name__)

    # Default data directory to the directory of this script combined with 'raw_data'.
    if not data_directory:
        data_directory = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "raw_data"
        )

    input_yaml_dir = os.path.join(data_directory, input_rel_dir)
    # Validate input directory exists
    if not os.path.exists(input_yaml_dir):
        logger.error(f"Input directory '{input_yaml_dir}' does not exist")
        raise ValueError(f"Input directory '{input_yaml_dir}' does not exist")

    output_yaml_dir = os.path.join(data_directory, output_rel_dir)
    if not os.path.exists(output_yaml_dir):
        logger.info(
            f"Output directory '{output_yaml_dir}' does not exist, creating it..."
        )
        os.makedirs(output_yaml_dir)

    counter = 0
    for yml_file_path in glob.glob(os.path.join(input_yaml_dir, "*.yaml")):
        try:
            yml_content = load_yaml(yml_file_path)
            parsed_yml_str = prase_yaml_completion(yml_content)
            yml_load = yaml.safe_load(parsed_yml_str)
            yml_file_name = os.path.basename(yml_file_path)
            save_yaml(yml_load, os.path.join(output_yaml_dir, yml_file_name))
            counter += 1
        except (ValueError, yaml.YAMLError) as exc:
            logger.error(
                f"Error parsing YAML string in {yml_file_path}: {exc}"
            )
            continue

    logger.info(f"Successfully parsed {counter} files")


if __name__ == "__main__":
    fire.Fire(run)
