# type: ignore
"""
YAML Table of Contents to Textbook Generator

WARNING - This script is very rough and needs significant enhancements to fully productionize
Description:
    This script processes YAML files and generates a detailed Table of Contents for a new textbook accompanying the course.

Usage:
    Command-line interface:
        $ python sciphi/examples/library_of_phi/gen_step4_draft_book.py run \
            --input_dir=table_of_contents  \
            --provider=openai \
            --model_name=gpt-4-0613 \
            --log_level=DEBUG
Parameters:
    provider (str): 
        The provider to use. Default is 'openai'.
    model_name (str): 
        The model_name to use. Default is 'gpt-3.5-turbo-instruct'.
    toc_dir (str): 
        Directory for the table of contents. Default is 'table_of_contents'.
    output_dir (str): 
        Directory for the output. Default is 'output_step_4'.
      (str): 
        Name of the textbook. Default is 'Introduction_to_Deep_Learning'.
    data_dir (Optional[str]):
        Directory where data is to be read from, defaults to `None`.
        When `None`, defaults to the `[Local Script Directory]/raw_data`
    max_related_context_to_sample (int): 
        Maximum context to sample. Default is 2000.
    max_prev_snippet_to_sample (int): 
        Maximum previous snippet to sample. Default is 2000.
    do_wiki (bool): 
        Whether to use Wikipedia. Default is True.
    wiki_server_url (str): 
        Wikipedia server URL. Uses environment variable "WIKI_SERVER_URL" if not provided.
    wiki_username (str): 
        Wikipedia username. Uses environment variable "WIKI_SERVER_USERNAME" if not provided.
    wiki_password (str): 
        Wikipedia password. Uses environment variable "WIKI_SERVER_PASSWORD" if not provided.
    log_level (str): 
        Logging level. Can be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL. Default is 'INFO'.
"""

import logging
import os
from typing import Generator, Tuple

import fire

from sciphi.examples.helpers import (
    get_default_settings_provider,
    load_yaml_file,
    wiki_search_api,
)
from sciphi.examples.library_of_phi.prompts import (
    BOOK_BULK_PROMPT,
    BOOK_CHAPTER_INTRODUCTION_PROMPT,
    BOOK_CHAPTER_SUMMARY_PROMPT,
    BOOK_FOREWARD_PROMPT,
)
from sciphi.writers import RawDataWriter

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


def get_key(config_dict: dict) -> str:
    """Get the key from a dictionary with a single key-value pair"""
    print("config_dict = ", config_dict)
    keys = list(config_dict.keys())
    if not keys:
        raise KeyError("Dictionary is empty, no key found")
    return keys[0]


def traverse_config(
    config: dict,
) -> Generator[Tuple[str, str, str, str, dict], None, None]:
    textbook_config = config[get_key(config)]
    textbook_name = get_key(textbook_config)

    chapter_configs = textbook_config[textbook_name][
        get_key(textbook_config[textbook_name])
    ]
    for chapter_config in chapter_configs:
        chapter_name = get_key(chapter_config)
        section_config = chapter_config[chapter_name]
        sections = section_config[get_key(section_config)]
        for section in sections:
            if isinstance(section, str):
                yield textbook_name, chapter_name, section, None, chapter_config

            elif isinstance(section, dict):
                section_name = get_key(section)
                subsection_config = section[section_name][
                    get_key(section[section_name])
                ]
                for subsection_name in subsection_config:
                    yield textbook_name, chapter_name, section_name, subsection_name, chapter_config


def save_progress(chapter, section, subsection, output):
    """Save progress to a file."""
    with open(f"{output}", "w") as f:
        f.write(f"{chapter}\n{section}\n{subsection or 'None'}")


def with_retry(func, max_retries=MAX_RETRIES):
    """Attempt to execute the provided function up to max_retries times."""
    for _ in range(max_retries):
        try:
            return func()
        except Exception as e:
            logging.warning(f"Exception encountered: {e}. Retrying...")
            time.sleep(5)
    raise ValueError(
        f"Failed to execute {func.__name__} after {max_retries} retries."
    )


class TextbookContentGenerator:
    """Generates textbook content from parsed course data."""

    def __init__(
        self,
        provider="openai",
        model_name="gpt-4-0613",
        data_dir=None,
        toc_dir="table_of_contents",
        output_dir="output_step_4",
        textbook="Introduction_to_Deep_Learning",
        max_related_context_to_sample=2_000,
        max_prev_snippet_to_sample=2_000,
        do_wiki=True,
        wiki_server_url=None,
        wiki_username=None,
        wiki_password=None,
        log_level="INFO",
    ):
        self.provider = provider
        self.model_name = model_name
        self.data_dir = data_dir or os.path.join(
            os.path.dirname(__file__), "raw_data"
        )
        self.toc_dir = toc_dir
        self.output_dir = output_dir
        self.textbook = textbook

        self.url = wiki_server_url or os.environ["WIKI_SERVER_URL"]
        self.username = wiki_username or os.environ["WIKI_SERVER_USERNAME"]
        self.password = wiki_password or os.environ["WIKI_SERVER_PASSWORD"]
        self.do_wiki = do_wiki

        if do_wiki and not self.url or not self.username or not self.password:
            raise ValueError(
                "Set do_wiki to `False`, or provide Wikipedia server url, username, and password."
            )

        # Constants for sampling
        self.max_related_context_to_sample = max_related_context_to_sample
        self.max_prev_snippet_to_sample = max_prev_snippet_to_sample
        logging.basicConfig(level=log_level.upper())

    def run(self):
        """Run the draft book generation process."""

        yml_file_path = os.path.join(
            self.data_dir, self.toc_dir, f"{self.textbook}.yaml"
        )
        yml_config = load_yaml_file(yml_file_path, do_prep=True)

        # Create an instance of the generator
        traversal_generator = traverse_config(yml_config)

        output_path = os.path.join(
            self.data_dir, self.output_dir, f"{self.textbook}.md"
        )
        llm_provider = get_default_settings_provider(
            provider=self.provider, model_name=self.model_name
        )
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))
        logger.info(f"Saving textbook to {output_path}")
        writer = RawDataWriter(output_path)
        writer.write("# NOTE - THIS TEXTBOOK WAS AI GENERATED\n")
        writer.write(
            "This textbook was generated using AI techniques. While it aims to be factual and accurate, please verify any critical information. The content may contain errors, biases or harmful content despite best efforts. Please report any issues.\n"
        )

        current_chapter = None
        prev_chapter_config = None
        chapter_intro_prompt = None
        logger.info("Looping over the textbook config...")
        do_skip = True

        for counter, elements in enumerate(traversal_generator):
            # elements is a tuple containing the names of textbook, chapter, section, and subsection.
            textbook, chapter, section, subsection, chapter_config = elements

            # Build the forward prompt
            if counter == 0:
                logger.info(f"Processing {textbook}, Chapter:{chapter}")
                logger.debug("Fetching related content..")
                related_context = (
                    wiki_search_api(
                        self.url, self.username, self.password, self.textbook
                    )
                    if self.do_wiki
                    else "Related context not available."
                )
                foreward_prompt = BOOK_FOREWARD_PROMPT.format(
                    title=textbook,
                    related_context=related_context[
                        : self.max_related_context_to_sample
                    ],
                )
                logger.debug(f"Constructing the foreward...")
                writer.write(f"# {textbook}\n")

                foreward = with_retry(
                    lambda: llm_provider.get_completion(foreward_prompt)
                )
                prev_response = foreward
                prev_chapter_config = chapter_config
                writer.write(f"{prev_response}\n")
                logger.info(f"Foreward Completion:\n{prev_response}\n\n")

            # Build the capter conclusion and next chapter introduction
            if chapter != current_chapter:
                if current_chapter is not None:
                    # Summarize the previous chapter
                    chapter_summary_prompt = BOOK_CHAPTER_SUMMARY_PROMPT.format(
                        title=textbook,
                        chapter=current_chapter,
                        book_context=f"Chapter outline:\n{str(prev_chapter_config)}",
                    )
                    chapter_completion = with_retry(
                        lambda: llm_provider.get_completion(
                            chapter_summary_prompt
                        )
                    )

                    prev_response = chapter_completion
                    writer.write(f"{prev_response}\n")
                    print(f"Chapter Conclusion:\n{prev_response}\n\n")

                # Introduce the new chapter
                chapter_intro_prompt = BOOK_CHAPTER_INTRODUCTION_PROMPT.format(
                    title=textbook,
                    chapter=chapter,
                    book_context=str(chapter_config),
                )
                chapter_introduction = with_retry(
                    lambda: llm_provider.get_completion(chapter_intro_prompt)
                )
                prev_response = chapter_introduction
                writer.write(f"{prev_response}\n")
                print(f"Chapter Introduction:\n{prev_response}\n\n")
                current_chapter = chapter

            related_context = (
                wiki_search_api(
                    self.url,
                    self.username,
                    self.password,
                    subsection or section,
                )
                if self.do_wiki
                else "Related context not available."
            )

            step_prompt = BOOK_BULK_PROMPT.format(
                title=textbook,
                chapter=chapter,
                section=section,
                subsection=subsection or "",
                related_context=related_context[
                    : self.max_related_context_to_sample
                ],
                book_context=prev_response[: self.max_prev_snippet_to_sample],
            )

            step_completion = with_retry(
                lambda: llm_provider.get_completion(step_prompt)
            )
            prev_response = step_completion
            writer.write(f"{step_completion}\n")
            save_progress(
                chapter,
                section,
                subsection,
                output_path.replace(".md", "_progress.txt"),
            )
        os.remove(output_path.replace(".md", "_progress.txt"))


if __name__ == "__main__":
    fire.Fire(TextbookContentGenerator)
