"""Generates textbook content from parsed course data."""
import logging
import multiprocessing
import os
from typing import Any, Generator, Tuple, Union

import fire

from sciphi.core.utils import get_data_dir
from sciphi.examples.helpers import (
    load_yaml_file,
    traverse_config,
    wiki_search_api,
    with_retry,
)
from sciphi.examples.library_of_phi.config_manager import ConfigurationManager
from sciphi.examples.library_of_phi.prompts import (
    BOOK_CHAPTER_BULK_PROMPT,
    BOOK_CHAPTER_INTRODUCTION_PROMPT,
    BOOK_CHAPTER_SUMMARY_PROMPT,
    BOOK_FOREWORD_PROMPT,
)
from sciphi.interface import InterfaceManager, ProviderName
from sciphi.llm import LLMConfigManager
from sciphi.writers import JsonlDataWriter, RawDataWriter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class TextbookContentGenerator:
    """Generates textbook content from parsed course data."""

    NO_RAG_TEXT = "Not currently available."
    AI_DISCLAIMER = "# NOTE - THIS TEXTBOOK WAS AI GENERATED\nThis textbook was generated using AI techniques. While it aims to be factual and accurate, please verify any critical information. The content may contain errors, biases or harmful content despite best efforts. Please report any issues.\n"

    class CompositeWriter:
        """Combines different writers for textbook generation."""

        def __init__(self, path: str) -> None:
            self.raw_writer = RawDataWriter(f"{path}.md")
            self.jsonl_writer = JsonlDataWriter(f"{path}.jsonl")

    def __init__(
        self,
        config_path: str = None,
        **cli_args,
    ) -> None:
        """Initialize the textbook content generator."""
        self._load_configuration(config_path, cli_args)

        provider_name = ProviderName(self.config.llm_provider)
        self.llm_provider = InterfaceManager.get_provider(
            provider_name,
            self.config.llm_model_name,
            LLMConfigManager.get_config_for_provider(provider_name).create(
                model_name=self.config.llm_model_name,
                max_tokens_to_sample=self.config.max_tokens_to_sample,
                temperature=self.config.temperature,
                top_k=self.config.top_k,
                port=cli_args.get("llm_port"),
            ),
        )
        self.logger = logging.getLogger("textbook_content_generator")
        self.logger.setLevel(self.config.log_level)
        if not self.config.skip_validation:
            self.config_manager.validate_config(self.logger)

    def _load_configuration(self, config_path: str, cli_args: dict):
        """Loads the configuration."""
        self.config_manager = ConfigurationManager(config_path)
        config = self.config_manager.load_config()

        # RAG settings
        config.rag_url = config.rag_server_url or os.environ.get(
            "RAG_SERVER_URL"
        )
        config.rag_username = config.rag_username or os.environ.get(
            "RAG_SERVER_USERNAME"
        )
        config.rag_password = config.rag_password or os.environ.get(
            "RAG_SERVER_PASSWORD"
        )
        config.num_threads_per_proc = (
            config.num_threads_per_proc or multiprocessing.cpu_count()
        )
        config.data_dir = config.data_dir or os.path.join(
            get_data_dir(), "library_of_phi"
        )
        config.update(cli_args)
        config.log_level = config.log_level.upper()

        if config.do_rag and not all(
            [config.rag_url, config.rag_username, config.rag_password]
        ):
            raise ValueError(
                "Set do_rag to `False`, or provide a RAG server rag_url, rag_username, and rag_password."
            )
        self.yml_pointer = config.batch_size
        self.config = config

    def get_writer(self, textbook_output_name: str) -> CompositeWriter:
        """Set up and return the output writer."""
        output_path = os.path.join(
            self.config.data_dir, self.config.output_dir, textbook_output_name
        )
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))
        self.logger.info(
            f"Saving textbook at {textbook_output_name} to {output_path}"
        )
        return TextbookContentGenerator.CompositeWriter(output_path)

    def dry_run(self) -> None:
        """
        Run a dry configuration validation without content
        generation and output summary statistics.
        Configuration is loaded and validated upstream in the constructor
        Validate LLM provider configuration
        """
        if not self.llm_provider:
            raise ValueError("Invalid LLM provider configuration.")

    def initialize_generators(
        self, yml_file_paths_chunk
    ) -> list[list[Union[Generator, Any]]]:
        """Initialize generators based on the yaml files."""
        generators = []
        for yml_file_path in yml_file_paths_chunk[0 : self.config.batch_size]:
            yml_config = load_yaml_file(yml_file_path)
            textbook_output_name = self.config.textbook or os.path.basename(
                yml_file_path
            ).replace(".yaml", "")
            writer = self.get_writer(textbook_output_name)
            generators.append(
                [self.process_book_elements(yml_config), None, writer]
            )
        return generators

    def process_single_generator(self, generator, current_completion, writer):
        """Process a single generator and fetch completions."""
        textbook, current_prompt, prompt_type, chapter, __ = generator.send(
            current_completion
        )
        self.logger.debug("-" * 200)
        self.logger.debug(f"Current Prompt:\n{current_prompt}\n\n")
        current_completion = with_retry(
            lambda: self.llm_provider.get_completion(current_prompt)
        )

        self.logger.debug(f"Current Completion:\n{current_completion}\n\n")
        self.logger.debug("-" * 200)
        if prompt_type == "foreword":
            writer.raw_writer.write(
                f"{TextbookContentGenerator.AI_DISCLAIMER}\n# {textbook}\n{current_completion}\n"
            )
        else:
            writer.raw_writer.write(f"{current_completion}\n")
        writer.jsonl_writer.write(
            [
                {
                    "prompt": current_prompt,
                    "completion": current_completion,
                    "type": prompt_type,
                }
            ]
        )
        return current_completion

    def get_next_generator(self, yml_file_paths_chunk: list[str]):
        """Get a generator for the next yml file."""
        if self.yml_pointer < len(yml_file_paths_chunk):
            yml_file_path = yml_file_paths_chunk[self.yml_pointer]
            textbook_output_name = os.path.basename(yml_file_path).replace(
                ".yaml", ""
            )
            yml_config = load_yaml_file(yml_file_path)
            self.yml_pointer += 1
            writer = self.get_writer(textbook_output_name)
            return [self.process_book_elements(yml_config), None, writer]
        return None

    def run(self):
        """Run the draft book generation process."""
        yml_file_paths_chunk = self.config_manager.get_yml_file_paths(
            self.logger
        )
        generators = self.initialize_generators(yml_file_paths_chunk)

        while generators:
            exhausted_generators = []

            for i, (generator, current_completion, writer) in enumerate(
                generators
            ):
                try:
                    updated_completion = self.process_single_generator(
                        generator, current_completion, writer
                    )
                    generators[i][1] = updated_completion
                except StopIteration:
                    exhausted_generators.append(i)

            # Remove exhausted generators and add new ones if there are still unprocessed yml files
            for index in reversed(exhausted_generators):
                del generators[index]

                new_generator = self.get_next_generator(yml_file_paths_chunk)
                if new_generator:
                    generators.append(new_generator)

    def process_book_elements(
        self, config: dict
    ) -> Generator[Tuple[str, str, str, str], None, None]:
        """Process the elements of a textbook configuration."""
        prev_chapter_config = None
        current_chapter = None

        for counter, elements in enumerate(traverse_config(config)):
            (
                textbook,
                chapter,
                section,
                subsection,
                chapter_config,
            ) = elements
            self.logger.debug(
                f"Iterating over {textbook}, {chapter}, {section}, {subsection}"
            )
            self.logger.debug(
                f"Generating step for {chapter} - {section} - {subsection}"
            )

            if counter == 0:
                current_prompt = self.construct_foreward_prompt(
                    textbook, chapter
                )
                prev_completion = (
                    yield textbook,
                    current_prompt,
                    "foreword",
                    current_chapter,
                    prev_chapter_config,
                )

            if chapter != current_chapter:
                # If we are past the foreword, write a chapter summary
                if current_chapter:
                    current_prompt = self.construct_summary_prompt(
                        textbook, chapter, prev_chapter_config
                    )
                prev_completion = (
                    yield textbook,
                    current_prompt,
                    "chapter_introduction",
                    current_chapter,
                    prev_chapter_config,
                )

                current_prompt = self.construct_intro_prompt(
                    textbook, chapter, chapter_config
                )
                prev_completion = (
                    yield textbook,
                    current_prompt,
                    current_chapter,
                    prev_chapter_config,
                    "chapter_conclusion",
                )

                current_chapter = chapter

            current_prompt = self.construct_step_prompt(
                textbook, chapter, section, subsection, prev_completion
            )
            prev_completion = (
                yield textbook,
                current_prompt,
                "chapter_bulk",
                current_chapter,
                prev_chapter_config,
            )

            prev_chapter_config = chapter_config

    def construct_foreward_prompt(
        self,
        textbook: str,
        chapter: str,
    ) -> Tuple[str, dict]:
        """Handle the foreword section and return the response and chapter configuration."""
        self.logger.info(f"Processing {textbook}, Chapter:{chapter}, Foreword")
        related_context = self._get_related_context(textbook)
        return BOOK_FOREWORD_PROMPT.format(
            title=textbook,
            related_context=related_context[
                : self.config.max_related_context_to_sample
            ],
        )

    def construct_intro_prompt(
        self,
        textbook: str,
        chapter: str,
        chapter_config: dict,
    ):
        self.logger.info(
            f"Processing {textbook}, Chapter:{chapter}, Introduction"
        )
        return BOOK_CHAPTER_INTRODUCTION_PROMPT.format(
            title=textbook,
            chapter=chapter,
            book_context=f"Chapter outline:\n{chapter_config}",
        )

    def construct_step_prompt(
        self,
        textbook: str,
        chapter: str,
        section: str,
        subsection: str,
        prev_completion: str,
    ):
        related_context = (
            self._get_related_context(subsection or section)
            if self.config.do_rag
            else TextbookContentGenerator.NO_RAG_TEXT
        )

        return BOOK_CHAPTER_BULK_PROMPT.format(
            title=textbook,
            chapter=chapter,
            section=section,
            subsection=subsection or "",
            related_context=related_context[
                : self.config.max_related_context_to_sample
            ],
            book_context=prev_completion[
                : self.config.max_prev_snippet_to_sample
            ],
        )

    def construct_summary_prompt(
        self,
        textbook: str,
        current_chapter: str,
        prev_chapter_config: dict,
    ):
        self.logger.info(
            f"Processing {textbook}, Chapter:{current_chapter}, Summary"
        )
        return BOOK_CHAPTER_SUMMARY_PROMPT.format(
            title=textbook,
            chapter=current_chapter,
            book_context=f"Chapter outline:\n{prev_chapter_config}",
        )

    def _get_related_context(self, query: str) -> str:
        """Retrieve related context from Wikipedia."""

        return with_retry(
            lambda: wiki_search_api(
                query,
                self.config.rag_url,
                self.config.rag_username,
                self.config.rag_password,
            )
        )


if __name__ == "__main__":
    fire.Fire(TextbookContentGenerator)
