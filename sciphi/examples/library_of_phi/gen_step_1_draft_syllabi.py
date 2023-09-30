# type: ignore
"""
MIT OCW Course Data Scraper to syllyabi 'Draft' YAML Generator

Description:
    This script is designed to scrape course data from the MIT OpenCourseWare (OCW) website and 
    generate input YAML files with the help of an LLM.

Usage:
    Command-line interface:
        $ python sciphi/examples/library_of_phi/gen_step_1_draft_syllabi.py run \
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
import textwrap
from glob import glob
from typing import Optional, Set

import fire
import yaml

from sciphi.interface import InterfaceManager, ProviderName
from sciphi.llm import LLMConfigManager

TOPIC_CREATION_PROMPT = textwrap.dedent(
    """
Take a deep breath, then closely examine the configuration that follows. You will be asked to produce a similar configuration as part of this task, so pay close attention to the format.

```yaml
course:
    Quantum Physics I:
        topics:
            - Basic Features of Quantum Mechanics:
                subtopics:
                    - Linearity
                    - Complex Numbers
                    - Non-deterministic
                    - Superposition
                    - Entanglement
            - Experimental Basis of Quantum Physics:
                subtopics:
                    - Two-slit Experiments
                    - Mach-Zehnder Interferometer
                    - Elitzur-Vaidman Bombs
                    - Photoelectric Effect
                    - Compton Scattering
                    - de Broglie Wavelength
            - Wave Mechanics:
                subtopics:
                    - Galilean Transformation of de Broglie Wavelength
                    - Wave-packets and Group Velocity
                    - Matter Wave for a Particle
                    - Momentum and Position Operators
                    - Schrödinger Equation
            - Interpretation of the Wavefunction:
                subtopics:
                    - Probability Density
                    - Probability Current
                    - Current Conservation
                    - Hermitian Operators
            - Expectation Values and Uncertainty:
                subtopics:
                    - Expectation Values of Operators
                    - Time Evolution of Wave-packets
                    - Fourier Transforms
                    - Parseval Theorem
                    - Uncertainty Relation
            - Quantum Physics in One-dimensional Potentials:
                subtopics:
                    - Stationary States
                    - Boundary Conditions
                    - Particle on a Circle
                    - Infinite Square Well
                    - Finite Square Well
                    - Semiclassical Approximations
                    - Numerical Solution by the Shooting Method
                    - Delta Function Potential
                    - Simple Harmonic Oscillator
                    - Reflection and Transmission Coefficients
                    - Ramsauer Townsend Effect
                    - 1D Scattering and Phase Shifts
                    - Levinson’s Theorem
            - Angular Momentum and Central Potentials:
                subtopics:
                    - Resonances and Breit-Wigner Distribution
                    - Central Potentials
                    - Algebra of Angular Momentum
                    - Legendre Polynomials
                    - Hydrogen Atom
                    - Energy Levels Diagram
                    - Virial Theorem
                    - Circular Orbits and Eccentricity
                    - Discovery of Spin
```

Given the following context, deduce the new configuration entry for the course "{course_name}". Be sure to fill in the appropriate topics and subtopics.

```md
{context}
```

Notes:
- Filter out any erroneous content like "QUIZ" or "TEST" that might appear in the syllabus. 
- Attempt to match the length and specificity of the above example; add your own context if necessary to accomplish this or remove extra context.
- You should target **5-10 main topics with 6-10 subtopics each**.

### Response:
"""
)


def extract_data_from_record(record: dict[str, str]) -> tuple[dict, str]:
    """Extract and organize data from a given record."""
    context = f"### Course Number:\n{record['course_number']}\n"
    context += f"### Course Name:\n{record['course_title']}\n"
    context += f"### Resource Level: {record['resource_level']}\n"
    topics = {}
    page_contents = record["page_contents"]

    for key in page_contents.keys():
        page = page_contents[key]
        context += f"## Page:\n{key}\n"
        if key != "syllabus":
            context += f"Text:\n{page['leading_text'][:500]}\n"
        else:
            topics = page["topics"]
        table = "\n".join([ele["topic"] for ele in page["table_rows"]])
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


class OCWScraper:
    """MIT OCW scraper class."""

    def __init__(
        self,
        provider: str = "openai",
        model_name: str = "gpt-4-0613",
        data_directory: Optional[str] = None,
        output_rel_dir: str = "output_step_1",
        input_jsonl_filename: str = "scraped_ocw.jsonl",
        prompt: str = TOPIC_CREATION_PROMPT,
        log_level: str = "INFO",
    ):
        self.provider = provider
        self.model_name = model_name
        self.data_directory = data_directory
        self.output_rel_dir = output_rel_dir
        self.input_jsonl_filename = input_jsonl_filename
        self.prompt = prompt
        logging.basicConfig(level=getattr(logging, log_level.upper()))

    def run(self):
        """Main function."""
        yaml.add_representer(str, quoted_presenter)

        provider_name = ProviderName(self.provider)
        llm_config = LLMConfigManager.get_config_for_provider(
            provider_name
        ).create(max_tokens_to_sample=None)
        llm_provider = InterfaceManager.get_provider(
            provider_name, self.model_name, llm_config
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
                    topics, context = extract_data_from_record(record)
                    mapped_topics = get_mapped_topics(topics)

                    if len(mapped_topics) != 3:
                        continue

                    category = (
                        mapped_topics["category"].lower().replace(" ", "_")
                    )
                    field = mapped_topics["field"].lower().replace(" ", "_")
                    subfield = (
                        mapped_topics["subfield"].lower().replace(" ", "_")
                    )
                    course_name = record["course_title"]

                    dump_name = f"field_{field}_subfield_{subfield}_course_name_{course_name.replace(' ','_')}"
                    observed_files = get_observed_files(output_dir)

                    if dump_name in observed_files:
                        logging.info(f"Skipping output file {dump_name}....")
                        continue

                    logging.info(f"Saving output file named {dump_name}.")
                    formatted_prompt = self.prompt.format(
                        course_name=course_name, context=context
                    )
                    completion = llm_provider.get_completion(formatted_prompt)
                    data_to_save = {
                        "completion": completion,
                        "discipline": category,
                        "resource_level": record["resource_level"],
                        "field": field,
                        "subfield": subfield,
                        "course_name": course_name,
                    }

                    with open(
                        os.path.join(output_dir, f"{dump_name}.yaml"),
                        "w",
                    ) as f:
                        yaml.dump(data_to_save, f, default_flow_style=False)

                except Exception as e:
                    logging.error(
                        f"Failed to create output yaml at {self.data_directory} with error: {e}"
                    )


if __name__ == "__main__":
    fire.Fire(OCWScraper)
