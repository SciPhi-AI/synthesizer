import glob
import multiprocessing
import os
from typing import Tuple

import fire
import yaml
from tqdm import tqdm

from sciphi.core.utils import (
    SciPhiConfig,
    get_config_dir,
    get_configured_logger,
    get_data_dir,
)
from sciphi.examples.helpers import (
    load_yaml_file,
    traverse_config,
    wiki_search_api,
    with_retry,
)
from sciphi.examples.library_of_phi.prompts import (
    BOOK_CHAPTER_BULK_PROMPT,
    BOOK_CHAPTER_INTRODUCTION_PROMPT,
    BOOK_CHAPTER_SUMMARY_PROMPT,
    BOOK_FOREWORD_PROMPT,
)
from sciphi.interface import InterfaceManager, ProviderName
from sciphi.llm import LLMConfigManager
from sciphi.writers import JsonlDataWriter, RawDataWriter


class TextbookContentGenerator:
    """Generates textbook content from parsed course data."""

    NO_WIKI_TEXT = "Not currently available."
    DEFAULT_SETTINGS_CONFIG = "book_draft_settings.yml"
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
        # Load the configuration
        with open(
            config_path
            or os.path.join(
                get_config_dir(),
                "generation_settings",
                TextbookContentGenerator.DEFAULT_SETTINGS_CONFIG,
            ),
            "r",
        ) as file:
            config = SciPhiConfig(yaml.safe_load(file))

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

        if config.do_rag and not all(
            [
                config.rag_url,
                config.rag_username,
                config.rag_password,
            ]
        ):
            raise ValueError(
                "Set do_rag to `False`, or provide a RAG server rag_url, rag_username, and rag_password."
            )

        provider_name = ProviderName(config.llm_provider)
        self.llm_provider = InterfaceManager.get_provider(
            provider_name,
            config.llm_model_name,
            LLMConfigManager.get_config_for_provider(provider_name).create(
                model_name=config.llm_model_name,
                max_tokens_to_sample=config.max_tokens_to_sample,
                temperature=config.temperature,
                top_k=config.top_k,
                port=cli_args.get("llm_port"),
            ),
        )
        self.config = config
        self.logger = get_configured_logger(__name__, config.log_level.upper())

    def initialize_processing(
        self, textbook_output_name: str
    ) -> CompositeWriter:
        """Set up and return the output writer."""
        output_path = os.path.join(
            self.config.data_dir, self.config.output_dir, textbook_output_name
        )
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))
        self.logger.info(f"Saving textbook to {output_path}")
        writer = TextbookContentGenerator.CompositeWriter(output_path)
        writer.raw_writer.write(TextbookContentGenerator.AI_DISCLAIMER)
        return writer

    def run(self) -> None:
        """Run the draft book generation process."""
        if self.config.textbook:
            yml_file_paths = [
                os.path.join(
                    self.config.data_dir,
                    self.config.toc_dir,
                    f"{self.config.textbook}.yaml",
                )
            ]
        else:
            yml_file_paths = glob.glob(
                os.path.join(
                    self.config.data_dir, self.config.toc_dir, "*.yaml"
                )
            )

        # Split the file paths into chunks for each process
        chunk_size = len(yml_file_paths) // self.config.num_processes
        start_idx = self.config.process_num * chunk_size
        if (
            self.config.process_num == self.config.num_processes - 1
        ):  # If it's the last process, it takes all remaining files
            end_idx = len(yml_file_paths)
        else:
            end_idx = start_idx + chunk_size
        yml_file_paths_chunk = yml_file_paths[start_idx:end_idx]

        # Filter out books that already exist in the target directory
        if self.config.filter_existing_books:
            filtered_books = []
            for yml_file_path in yml_file_paths_chunk:
                if not self.book_exists(yml_file_path):
                    filtered_books.append(yml_file_path)
                else:
                    self.logger.warning(
                        f"Skipping {yml_file_path} as it already exists."
                    )
            yml_file_paths_chunk = filtered_books

        if self.config.num_threads_per_proc > 1:
            self.logger.debug(
                f"Process {self.config.process_num} is processing {len(yml_file_paths_chunk)} files"
            )

            # Use multiprocessing to parallelize the processing of files in the chunk
            pool = multiprocessing.Pool(
                processes=self.config.num_threads_per_proc
            )
            # Wrap yml_file_paths_chunk with tqdm
            with tqdm(
                total=len(yml_file_paths_chunk), desc="Processing files"
            ) as pbar:
                for _ in pool.imap(
                    self.process_yml_file, yml_file_paths_chunk
                ):
                    pbar.update(1)

            pool.close()
            pool.join()
        else:
            self.process_yml_file(yml_file_paths_chunk[0])

    def get_related_context(self, query: str) -> str:
        """Retrieve related context from Wikipedia."""

        return with_retry(
            lambda: wiki_search_api(
                query,
                self.config.rag_url,
                self.config.rag_username,
                self.config.rag_password,
            )
        )

    def book_exists(self, yml_path: str) -> bool:
        """Check if the book for the given YAML file exists in the output directory."""
        book_name = os.path.splitext(os.path.basename(yml_path))[
            0
        ]  # Extract the book name from the YAML file name

        # Assume the book files in the output directory have the ".md" extension
        output_path = os.path.join(
            self.config.data_dir, self.config.output_dir, f"{book_name}.md"
        )
        return os.path.exists(output_path)

    def process_yml_file(self, yml_file_path: str) -> None:
        """Process a single YAML file to generate textbook content."""
        try:
            textbook_output_name = self.config.textbook or os.path.basename(
                yml_file_path
            ).replace(".yaml", "")
            self.logger.debug(f"Processing {yml_file_path}")
            yml_config = load_yaml_file(yml_file_path)

            writer = self.initialize_processing(textbook_output_name)

            prev_chapter_config = None
            current_chapter = None
            for counter, elements in enumerate(traverse_config(yml_config)):
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
                    prev_response = self.handle_foreword(
                        writer, textbook, chapter
                    )

                if chapter != current_chapter:
                    prev_response = self.handle_chapter_transition(
                        writer,
                        textbook,
                        chapter,
                        current_chapter,
                        chapter_config,
                        prev_chapter_config,
                    )
                    current_chapter = chapter

                related_context = (
                    self.get_related_context(subsection or section)
                    if self.config.do_rag
                    else TextbookContentGenerator.NO_WIKI_TEXT
                )
                step_prompt = self._build_step_prompt(
                    textbook,
                    chapter,
                    section,
                    subsection,
                    related_context,
                    prev_response,
                )
                self.logger.debug(f"The prompt for this step:\n{step_prompt}")
                step_completion = self.llm_provider.get_completion(step_prompt)

                self.logger.debug(
                    f"The completion for this step:\n{step_completion}"
                )

                prev_response = step_completion
                writer.raw_writer.write(f"{step_completion}\n")
                writer.jsonl_writer.write(
                    [
                        {
                            "prompt": step_prompt,
                            "completion": step_completion,
                            "type": "step_completion",
                        }
                    ]
                )
                prev_chapter_config = chapter_config
        except Exception as e:
            self.logger.error("Error processing file with {e}")
            return

    def handle_foreword(
        self,
        writer: CompositeWriter,
        textbook: str,
        chapter: str,
    ) -> Tuple[str, dict]:
        """Handle the foreword section and return the previous response and chapter configuration."""
        self.logger.info(f"Processing {textbook}, Chapter:{chapter}")
        related_context = self.get_related_context(textbook)
        foreword_prompt = BOOK_FOREWORD_PROMPT.format(
            title=textbook,
            related_context=related_context[
                : self.config.max_related_context_to_sample
            ],
        )
        print("foreword_prompt = ", foreword_prompt)
        self.logger.debug(f"Prompting a foreword with:\n{foreword_prompt}\n\n")
        foreword_completion = self.llm_provider.get_completion(foreword_prompt)
        self.logger.debug(f"Authored a foreword:\n{foreword_completion}\n\n")
        print("foreword_completion = ", foreword_completion)

        writer.raw_writer.write(f"# {textbook}\n{foreword_completion}\n")
        writer.jsonl_writer.write(
            [
                {
                    "prompt": foreword_prompt,
                    "completion": foreword_completion,
                    "type": "foreword",
                }
            ]
        )

        return foreword_completion

    def handle_chapter_transition(
        self,
        writer: CompositeWriter,
        textbook: str,
        chapter: str,
        current_chapter: str,
        chapter_config: dict,
        prev_chapter_config: dict,
    ) -> str:
        """Handle chapter transitions and return the previous response."""
        # If we are past the foreword, write a chapter summary
        if current_chapter:
            chapter_summary_prompt = BOOK_CHAPTER_SUMMARY_PROMPT.format(
                title=textbook,
                chapter=current_chapter,
                book_context=f"Chapter outline:\n{prev_chapter_config}",
            )
            self.logger.debug(
                f"Prompting a conclusion with:\n{chapter_summary_prompt}\n\n"
            )

            chapter_conclusion = self.llm_provider.get_completion(
                chapter_summary_prompt
            )
            self.logger.debug(
                f"Authored a chapter completion:\n{chapter_conclusion}\n\n"
            )

            writer.raw_writer.write(f"{chapter_conclusion}\n")
            writer.jsonl_writer.write(
                [
                    {
                        "prompt": chapter_summary_prompt,
                        "completion": chapter_conclusion,
                        "type": "chapter_intro",
                    }
                ]
            )

        chapter_intro_prompt = BOOK_CHAPTER_INTRODUCTION_PROMPT.format(
            title=textbook,
            chapter=chapter,
            book_context=f"Chapter outline:\n{chapter_config}",
        )
        self.logger.debug(
            f"Prompting an introduction with:\n{chapter_intro_prompt}\n\n"
        )

        chapter_introduction = self.llm_provider.get_completion(
            chapter_intro_prompt
        )
        self.logger.debug(
            f"Authored a chapter introduction:\n{chapter_introduction}\n\n"
        )

        writer.raw_writer.write(f"{chapter_introduction}\n")
        writer.jsonl_writer.write(
            [
                {
                    "prompt": chapter_intro_prompt,
                    "completion": chapter_introduction,
                    "type": "chapter_summary",
                }
            ]
        )
        return chapter_introduction

    def _build_step_prompt(
        self,
        textbook: str,
        chapter: str,
        section: str,
        subsection: str,
        related_context: str,
        prev_response: str,
    ) -> str:
        """Build and return the step prompt."""
        return BOOK_CHAPTER_BULK_PROMPT.format(
            title=textbook,
            chapter=chapter,
            section=section,
            subsection=subsection or "",
            related_context=related_context[
                : self.config.max_related_context_to_sample
            ],
            book_context=prev_response[
                : self.config.max_prev_snippet_to_sample
            ],
        )


if __name__ == "__main__":
    fire.Fire(TextbookContentGenerator)
