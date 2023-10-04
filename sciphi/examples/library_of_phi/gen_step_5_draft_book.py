# type: ignore
"""
YAML Table of Contents to Textbook Generator

WARNING - This script is very rough and needs significant enhancements to fully productionize
Description:
    This script processes YAML files and generates a detailed Table of Contents for a new textbook accompanying the course.

Usage:
    Command-line interface:
        $ python sciphi/examples/library_of_phi/gen_step_5_draft_book.py run \
            --input_dir=output_step_4  \
            --provider=openai \
            --model_name=gpt-4-0613 \
            --log_level=DEBUG
Parameters:
    provider (str): 
        The provider to use. Default is 'openai'.
    model_name (str): 
        The model_name to use. Default is 'gpt-4-0613'.
    toc_dir (str): 
        Directory for the table of contents. Default is 'output_step_4'.
    output_dir (str): 
        Directory for the output. Default is 'output_step_5'.
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
    num_threads (int):
        Number of threads to use. Defaults to the number of CPUs available.
"""
import glob
import logging
import multiprocessing
import os
from typing import Tuple

import fire

from sciphi.examples.helpers import (
    get_default_settings_provider,
    load_yaml_file,
    traverse_config,
    wiki_search_api,
    with_retry,
)
from sciphi.examples.library_of_phi.prompts import (
    BOOK_BULK_PROMPT,
    BOOK_CHAPTER_INTRODUCTION_PROMPT,
    BOOK_CHAPTER_SUMMARY_PROMPT,
    BOOK_FOREWARD_PROMPT,
)
from sciphi.writers import RawDataWriter


def save_progress(chapter: str, section: str, subsection: str, output: str):
    """Save progress to a file."""
    with open(f"{output}", "w") as f:
        f.write(f"{chapter}\n{section}\n{subsection or 'None'}")


def load_progress(output_path: str) -> Tuple[str, str, str]:
    """Load progress from a saved file."""
    progress_file = output_path.replace(".md", "_progress.txt")
    if os.path.exists(progress_file):
        with open(progress_file, "r") as f:
            chapter = f.readline().strip()
            section = f.readline().strip()
            subsection = f.readline().strip() or None
        return chapter, section, subsection
    return None, None, None


def get_wiki_related_context(
    query: str, url: str, username: str, password: str, do_wiki: bool
) -> str:
    """Retrieve related context from Wikipedia."""
    return (
        wiki_search_api(url, username, password, query)
        if do_wiki
        else "Related context not available."
    )


def setup_logging(log_level="INFO"):
    """Set up logging."""
    logging.basicConfig(level=log_level.upper())
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level.upper())
    return logger


class TextbookContentGenerator:
    """Generates textbook content from parsed course data."""

    NO_WIKI_TEXT = "Not currently available."

    def __init__(
        self,
        provider="openai",
        model_name="gpt-4-0613",
        data_dir=None,
        toc_dir="output_step_4",
        output_dir="output_step_5",
        max_related_context_to_sample=2_000,
        max_prev_snippet_to_sample=2_000,
        do_wiki=True,
        wiki_server_url=None,
        wiki_username=None,
        wiki_password=None,
        textbook=None,
        log_level="INFO",
        num_threads=None,
    ) -> None:
        self.provider = provider
        self.model_name = model_name
        self.llm_provider = get_default_settings_provider(
            provider=self.provider, model_name=self.model_name
        )

        self.data_dir = data_dir or os.path.join(
            os.path.dirname(__file__), "raw_data"
        )
        self.toc_dir = toc_dir
        self.output_dir = output_dir
        self.textbook = textbook
        self.url = wiki_server_url or os.environ.get("WIKI_SERVER_URL")
        self.username = wiki_username or os.environ.get("WIKI_SERVER_USERNAME")
        self.password = wiki_password or os.environ.get("WIKI_SERVER_PASSWORD")
        self.do_wiki = do_wiki
        self.log_level = log_level.upper()
        self.max_related_context_to_sample = max_related_context_to_sample
        self.max_prev_snippet_to_sample = max_prev_snippet_to_sample

        self.num_threads = num_threads or multiprocessing.cpu_count()

        if self.do_wiki and not all([self.url, self.username, self.password]):
            raise ValueError(
                "Set do_wiki to `False`, or provide Wikipedia server url, username, and password."
            )

        # Constants for sampling
        self.max_related_context_to_sample = max_related_context_to_sample
        self.max_prev_snippet_to_sample = max_prev_snippet_to_sample

        setup_logging(log_level=self.log_level).debug(
            "Finishing initialization"
        )

    @property
    def logger(self) -> logging.Logger:
        return setup_logging(log_level=self.log_level)

    def run(self) -> None:
        """Run the draft book generation process."""
        if self.textbook:
            yml_file_paths = [
                os.path.join(
                    self.data_dir, self.toc_dir, f"{self.textbook}.yaml"
                )
            ]
        else:
            yml_file_paths = glob.glob(
                os.path.join(self.data_dir, self.toc_dir, "**/**/*.yaml")
            )[0:1]

        self.logger.debug(
            f"Running process over a total of {len(yml_file_paths)} files"
        )

        # Use multiprocessing to parallelize the processing of multiple YAML files
        pool = multiprocessing.Pool(processes=self.num_threads)
        pool.map(self.process_yml_file, yml_file_paths)
        pool.close()
        pool.join()

    def process_yml_file(self, yml_file_path: str):
        """Process a single YAML file to generate textbook content."""
        textbook_output_name = self.textbook or os.path.basename(
            yml_file_path
        ).replace(".yaml", "")
        self.logger.debug(f"Processing {yml_file_path}")
        yml_config = load_yaml_file(yml_file_path)

        (
            output_path,
            writer,
            last_chapter,
            last_section,
            last_subsection,
        ) = self.initialize_processing(textbook_output_name)

        traversal_generator = traverse_config(yml_config)
        prev_chapter_config = None
        current_chapter = None
        for counter, elements in enumerate(traversal_generator):
            textbook, chapter, section, subsection = elements
            start_flag = self.update_start_flag(
                chapter,
                section,
                subsection,
                last_chapter,
                last_section,
                last_subsection,
            )

            if not start_flag:
                continue

            self.logger.debug(
                f"Generating step for {chapter} - {section} - {subsection}"
            )

            if counter == 0:
                prev_response, prev_chapter_config = self.handle_foreword(
                    writer, textbook, chapter, prev_chapter_config
                )

            if chapter != current_chapter:
                prev_response = self.handle_chapter_transition(
                    writer,
                    textbook,
                    chapter,
                    current_chapter,
                    prev_chapter_config,
                )
                current_chapter = chapter

            related_context = (
                self.get_related_context(subsection or section)
                if self.do_wiki
                else TextbookContentGenerator.NO_WIKI_TEXT
            )
            step_prompt = self.build_step_prompt(
                textbook,
                chapter,
                section,
                subsection,
                related_context,
                prev_response,
            )

            step_completion = self.persistent_completion(step_prompt)
            prev_response = step_completion
            writer.write(f"{step_completion}\n")

            self.save_current_progress(
                chapter, section, subsection, output_path
            )

        # os.remove(output_path.replace(".md", "_progress.txt"))

    def setup_output_writer(
        self, textbook_name: str
    ) -> Tuple[str, RawDataWriter]:
        """Set up and return the output writer."""
        output_path = os.path.join(
            self.data_dir, self.output_dir, f"{textbook_name}.md"
        )
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))
        self.logger.info(f"Saving textbook to {output_path}")
        writer = RawDataWriter(output_path)
        writer.write("# NOTE - THIS TEXTBOOK WAS AI GENERATED\n")
        writer.write(
            "This textbook was generated using AI techniques. While it aims to be factual and accurate, please verify any critical information. The content may contain errors, biases or harmful content despite best efforts. Please report any issues.\n"
        )
        return output_path, writer

    def handle_foreword(
        self,
        writer: RawDataWriter,
        textbook: str,
        chapter: str,
        prev_chapter_config: dict,
    ) -> Tuple[str, dict]:
        """Handle the foreword section and return the previous response and chapter configuration."""
        self.logger.info(f"Processing {textbook}, Chapter:{chapter}")
        related_context = self.get_related_context(textbook)
        foreward_prompt = BOOK_FOREWARD_PROMPT.format(
            title=textbook,
            related_context=related_context[
                : self.max_related_context_to_sample
            ],
        )
        self.logger.debug("Constructing the foreward...")
        writer.write(f"# {textbook}\n")
        foreward = self._progress_textbook(
            foreward_prompt, writer, "Authored a foreward:\n"
        )
        return foreward, prev_chapter_config

    def handle_chapter_transition(
        self,
        writer: RawDataWriter,
        textbook: str,
        chapter: str,
        current_chapter: str,
        prev_chapter_config: dict,
    ) -> str:
        """Handle chapter transitions and return the previous response."""
        if current_chapter:
            chapter_summary_prompt = BOOK_CHAPTER_SUMMARY_PROMPT.format(
                title=textbook,
                chapter=current_chapter,
                book_context=f"Chapter outline:\n{prev_chapter_config}",
            )
            chapter_completion = self._progress_textbook(
                chapter_summary_prompt,
                writer,
                "Authored a chapter conclusion:\n",
            )
            writer.write(f"{chapter_completion}\n")

        chapter_intro_prompt = BOOK_CHAPTER_INTRODUCTION_PROMPT.format(
            title=textbook,
            chapter=chapter,
            book_context=str(prev_chapter_config),
        )
        chapter_introduction = self.persistent_completion(chapter_intro_prompt)
        self.logger.debug(
            f"Authored a chapter introduction:\n{chapter_introduction}\n\n"
        )
        writer.write(f"{chapter_introduction}\n")
        return chapter_introduction

    def get_related_context(self, query: str) -> str:
        """Retrieve related context from Wikipedia."""
        return get_wiki_related_context(
            query, self.url, self.username, self.password, self.do_wiki
        )

    def build_step_prompt(
        self,
        textbook: str,
        chapter: str,
        section: str,
        subsection: str,
        related_context: str,
        prev_response: str,
    ) -> str:
        """Build and return the step prompt."""
        return BOOK_BULK_PROMPT.format(
            title=textbook,
            chapter=chapter,
            section=section,
            subsection=subsection or "",
            related_context=related_context[
                : self.max_related_context_to_sample
            ],
            book_context=prev_response[: self.max_prev_snippet_to_sample],
        )

    def save_current_progress(
        self, chapter: str, section: str, subsection: str, output_path: str
    ):
        """Save the current progress."""
        save_progress(
            chapter,
            section,
            subsection,
            output_path.replace(".md", "_progress.txt"),
        )

    def persistent_completion(self, prompt: str) -> str:
        return with_retry(lambda: self.llm_provider.get_completion(prompt))

    def initialize_processing(self, textbook_output_name):
        """Initialize processing by setting up the writer and loading progress."""
        output_path, writer = self.setup_output_writer(textbook_output_name)
        last_chapter, last_section, last_subsection = load_progress(
            output_path
        )
        return output_path, writer, last_chapter, last_section, last_subsection

    def update_start_flag(
        self,
        chapter,
        section,
        subsection,
        last_chapter,
        last_section,
        last_subsection,
    ):
        """Update the start flag based on the last processed element."""
        if not last_chapter:
            return True
        return (
            chapter == last_chapter
            and section == last_section
            and (last_subsection == "None" or subsection == last_subsection)
        )

    def _progress_textbook(
        self, prompt: str, writer: RawDataWriter, log_message: str
    ):
        """Progress the textbook generation."""
        result = self.persistent_completion(prompt)
        writer.write(f"{result}\n")
        self.logger.debug(f"{log_message}{result}\n\n")
        return result


if __name__ == "__main__":
    fire.Fire(TextbookContentGenerator)
