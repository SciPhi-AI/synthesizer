"""
MIT OCW Course Data Scraper to YAML

Description:
    This script is designed to scrape course data from the MIT OpenCourseWare (OCW) website and 
    generate YAML files suitable for LLM (Language Learning Model).

Usage:
    Command-line interface:
        $ python sciphi/examples/library_of_phi/yaml_step_2.py \
            --output_dir=my_output_directory \
            --input_filename=my_input_file.jsonl \
            --log_level=DEBUG
Parameters:
    input_rel_dir (str): 
        The folder for the input JSONL files containing the first pass YAML data. 

    output_rel_dir (str): 
        The directory where the parsed YAML files will be saved. 

    data_directory (Optional[str]): 
        The directory where the input JSONL file is located. 
        If not specified, the default location is the directory of this script combined with 'raw_data'.

    log_level (str): 
        Logging level for the scraper. Can be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL. 
        Default is 'INFO'.
"""
import glob
import logging
import os

import fire
import yaml


def load_yaml(yml_file):
    """Load the content of a YAML file."""
    with open(yml_file, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def save_yaml(content, filename):
    """Save content to a YAML file."""
    with open(filename, "w", encoding="utf-8") as file:
        yaml.dump(content, file, allow_unicode=True)


def parse_yaml_content(yml_content):
    """Parse and clean YAML content."""
    completion = yml_content.get("completion", "")
    if "```yaml" not in completion:
        raise ValueError("YML not found in completion")

    yml_str = completion.split("```yaml")[1].split("```")[0]

    return clean_yaml_string(yml_str)


def clean_yaml_string(yml_str):
    """Clean and format the YAML string."""
    parsed_yml_str = ""
    split_lines = yml_str.splitlines()

    for it, line in enumerate(split_lines):
        line = replace_special_characters(line)
        line = format_yaml_line(line, it, split_lines)
        parsed_yml_str += line + "\n"

    return parsed_yml_str


def replace_special_characters(line):
    """Replace special characters in the YAML string."""
    replacements = {
        "\u201C": '"',
        "\u201D": '"',
        "Ã©": "é",
        "Å": "œ",
        "â": "",
        "Î©": "I",
        "Ï": "I",
        "\x83": "",
        "\x88": "",
        "\x89": "",
        "\x90": "",
        "\x91": "",
        "\x92": "",
        "\x9b": "",
        "\x8f": "",
    }
    for old, new in replacements.items():
        line = line.replace(old, new)

    line = line.replace("\\", "\\\\")
    line = line.replace('"', "'")

    return line


def format_yaml_line(line, index, split_lines):
    """Format a specific line in the YAML content."""
    line_cut = line.find("- ")
    if line_cut != -1:
        end = len(line) if line[-1] != ":" else len(line) - 1
        line = (
            line[: line_cut + 2]
            + '"'
            + line[line_cut + 2 : end]
            + '"'
            + ("" if end == len(line) else ":")
        )
        if line[-1] != ":" and index != len(split_lines) - 1:
            if "subtopics:" in split_lines[index + 1]:
                line += ":"
    elif index == 2:
        first_non_blank_char = next(
            (i for i, char in enumerate(line) if char != " "), 0
        )
        if first_non_blank_char != 0:
            line = (
                line[:first_non_blank_char]
                + '"'
                + line[first_non_blank_char:-1]
                + '":'
            )
    return line


def run(
    input_rel_dir="yaml_step_1",
    output_rel_dir="yaml_step_2",
    data_directory=None,
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
            parsed_yml_str = parse_yaml_content(yml_content)
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
