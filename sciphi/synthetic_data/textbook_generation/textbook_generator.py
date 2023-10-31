"""Generates textbook content from parsed course data."""
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Generator, Optional, Tuple

from sciphi.core import LLMProviderName, RAGProviderName
from sciphi.core.writers import JsonlDataWriter, RawDataWriter
from sciphi.interface import LLMInterfaceManager, RAGInterfaceManager
from sciphi.interface.llm.sciphi_interface import SciPhiFormatter
from sciphi.llm import GenerationConfig
from sciphi.synthetic_data.textbook_generation.helpers import (
    load_yaml_file,
    with_retry,
)
from sciphi.synthetic_data.textbook_generation.prompts import (
    BOOK_CHAPTER_BULK_PROMPT,
    BOOK_CHAPTER_CONCLUSION_PROMPT,
    BOOK_CHAPTER_INTRODUCTION_PROMPT,
    BOOK_FOREWORD_PROMPT,
)
from sciphi.synthetic_data.textbook_generation.textbook_config import (
    ConfigurationManager,
    traverse_textbook_config,
)

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
        config_path: Optional[str] = None,
        **cli_args,
    ) -> None:
        """Initialize the textbook content generator."""
        self._load_configuration(config_path, cli_args)

        self.rag_interface = (
            RAGInterfaceManager.get_interface_from_args(
                RAGProviderName(self.config.rag_provider_name),
                api_base=self.config.rag_api_base or self.config.llm_api_base,
                api_key=self.config.rag_api_key or self.config.llm_api_key,
                top_k=self.config.rag_top_k,
            )
            if self.config.rag_enabled
            else None
        )
        self.llm_interface = LLMInterfaceManager.get_interface_from_args(
            LLMProviderName(self.config.llm_provider_name),
            api_key=self.config.llm_api_key,
            api_base=self.config.llm_api_base,
            # Currently only consumed by SciPhi
            rag_interface=self.rag_interface,
            # Consumed by single-load providers
            model_name=self.config.llm_model_name,
        )

        self.generation_config = GenerationConfig(
            temperature=self.config.llm_temperature,
            top_k=self.config.llm_top_k,
            max_tokens_to_sample=self.config.llm_max_tokens_to_sample,
            model_name=self.config.llm_model_name,
            skip_special_tokens=self.config.llm_skip_special_tokens,
            stop_token=SciPhiFormatter.INIT_PARAGRAPH_TOKEN,
        )

        self.logger = logging.getLogger("textbook_content_generator")
        self.logger.setLevel(self.config.log_level)
        if not self.config.skip_validation:
            self.config_manager.validate_config(self.logger)

    def _load_configuration(self, config_path: Optional[str], cli_args: dict):
        """Loads the configuration."""
        self.config_manager = ConfigurationManager(config_path)
        config = self.config_manager.load_config()

        # RAG settings
        config.rag_api_base = config.rag_api_base or os.environ.get(
            "RAG_API_BASE"
        )
        config.rag_api_key = config.rag_api_key or os.environ.get(
            "RAG_API_KEY"
        )
        config.data_dir = config.data_dir or os.getcwd()
        config.update(cli_args)
        config.log_level = config.log_level.upper()
        config.max_threads = config.max_threads or os.cpu_count()

        if config.rag_enabled and not all(
            [config.rag_api_base, config.rag_api_key]
        ):
            raise ValueError(
                "Set do_rag to `False`, or provide a RAG server rag_api_base and rag_api_key."
            )
        self.yml_pointer = 0
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
        if not self.llm_interface:
            raise ValueError("Invalid LLM provider configuration.")

    def run(self) -> None:
        """Run the draft book generation process."""
        yml_file_paths_chunk = self.config_manager.get_yml_file_paths(
            self.logger
        )
        self.generators = self.initialize_generators(yml_file_paths_chunk)
        self.logger.info(
            f"Starting the generation process with {len(self.generators)} generators"
        )
        while self.generators:
            current_iteration, prompt_indices = self._process_iteration()
            current_completions = self._fetch_completions(
                current_iteration, prompt_indices
            )
            self._handle_generators(current_iteration, current_completions)
            self._manage_generators(yml_file_paths_chunk, current_iteration)

    def initialize_generators(
        self, yml_file_paths_chunk: list[str]
    ) -> list[
        tuple[Generator[dict, None, None], Optional[str], CompositeWriter]
    ]:
        """Initialize generators based on the yaml files."""
        return [
            ele
            for ele in [
                self._get_next_generator(yml_file_paths_chunk)
                for _ in range(
                    min(self.config.batch_size, len(yml_file_paths_chunk))
                )
            ]
            if ele is not None
        ]

    def _get_next_generator(
        self, yml_file_paths_chunk: list[str]
    ) -> Optional[
        tuple[Generator[dict, None, None], Optional[str], CompositeWriter]
    ]:
        """Get a generator for the next yml file."""
        if self.yml_pointer < len(yml_file_paths_chunk):
            yml_file_path = yml_file_paths_chunk[self.yml_pointer]
            textbook_output_name = os.path.basename(yml_file_path).replace(
                ".yaml", ""
            )
            yml_config = load_yaml_file(yml_file_path)
            self.yml_pointer += 1
            return (
                self.process_book_elements(yml_config),
                None,
                self.get_writer(textbook_output_name),
            )
        return None

    def _worker(
        self, i: int, generator, current_completion
    ) -> Tuple[int, Optional[dict], int]:
        try:
            current_iteration = generator.send(current_completion)
            return i, current_iteration, i
        except StopIteration:
            return i, None, i

    def _process_iteration(self) -> Tuple[list[Optional[dict]], list[int]]:
        """Process a single iteration of the generators."""
        current_iterations: list[Optional[dict]] = [None] * len(
            self.generators
        )
        prompts_for_completion = []
        prompt_indices = []

        with ThreadPoolExecutor(self.config.max_threads) as executor:
            futures = [
                executor.submit(self._worker, i, generator, current_completion)
                for i, (generator, current_completion, _) in enumerate(
                    self.generators
                )
            ]

            for future in futures:
                i, iteration, idx = future.result()
                current_iterations[i] = iteration
                if iteration is not None:
                    prompts_for_completion.append(iteration["prompt"])
                    prompt_indices.append(idx)

        return current_iterations, prompt_indices

    def _fetch_completions(
        self,
        current_iterations: list[Optional[dict]],
        prompt_indices: list[int],
    ) -> list[Optional[str]]:
        """Fetch completions for the current iteration."""
        prompts_for_completion = [x["prompt"] for x in current_iterations if x]
        fetched_completions = self.llm_interface.get_batch_completion(
            prompts_for_completion, self.generation_config
        )
        current_completions: list[Optional[str]] = [None] * len(
            current_iterations
        )
        for idx, completion in zip(prompt_indices, fetched_completions):
            current_completions[idx] = completion
        return current_completions

    def _handle_generators(
        self,
        current_iterations: list[Optional[dict]],
        current_completions: list[Optional[str]],
    ) -> None:
        """Handle the generators, logging and updating current state."""
        for i, (_, __, writer) in enumerate(self.generators):
            current_iteration: Optional[dict] = current_iterations[i]
            if current_iteration is None:
                continue
            current_iteration["completion"] = current_completions[i]

            self._log_current_state(current_iteration)
            self._write_content(writer, current_iteration)
            self.generators[i] = (
                self.generators[i][0],
                current_completions[i],
                self.generators[i][2],
            )

    def _write_content(
        self,
        writer: CompositeWriter,
        current_iteration: dict,
    ):
        """Write the content to the writer."""
        # Special treatment for the foreword
        if current_iteration["prompt_type"] == "foreword":
            writer.raw_writer.write(
                f"{TextbookContentGenerator.AI_DISCLAIMER}\n# {current_iteration['textbook']}\n"
            )
        writer.raw_writer.write(f"{current_iteration['completion']}\n")

        writer.jsonl_writer.write([current_iteration])

    def _manage_generators(
        self,
        yml_file_paths_chunk: list[str],
        current_iterations: list[Optional[dict]],
    ):
        """Manage the generators, removing exhausted ones and adding new ones."""
        exhausted_generators = [
            i for i, item in enumerate(current_iterations) if item is None
        ]

        for index in reversed(exhausted_generators):
            del self.generators[index]
            new_generator = self._get_next_generator(yml_file_paths_chunk)
            if new_generator:
                self.generators.append(new_generator)

    def _log_current_state(self, current_iteration: dict) -> None:
        """Log the current state of the generator."""
        self.logger.debug("-" * 200)
        self.logger.debug(
            f"Current Prompt:\n{current_iteration['prompt']}\n\n"
        )
        self.logger.debug(
            f"Current Completion:\n{current_iteration['completion']}\n\n"
        )
        self.logger.debug("-" * 200)

    def process_book_elements(
        self, config: dict
    ) -> Generator[dict, None, None]:
        """Process the elements of a textbook configuration."""

        def _construct_return_dict(
            textbook: str,
            prompt_type: str,
            chapter: str,
            section: str,
            subsection: str,
            prev_chapter_config: Optional[dict],
            prompt: str,
            related_context: str,
            book_context: str,
        ) -> dict:
            return {
                "textbook": textbook,
                "prompt_type": prompt_type,
                "chapter": chapter,
                "section": section,
                "subsection": subsection,
                "prev_chapter_config": prev_chapter_config,
                "prompt": prompt,
                "related_context": related_context,
                "book_context": book_context,
            }

        def step_iterator(
            textbook: str,
            chapter: str,
            chapter_config: dict,
            section: str,
            subsection: str,
            prev_completion: Optional[str],
            prev_chapter_config: Optional[dict],
            prompt_type: str,
        ):
            prompt, related_context, book_context = self.construct_prompt(
                textbook,
                chapter,
                chapter_config,
                section,
                subsection,
                prev_completion,
                prev_chapter_config,
                prompt_type,
            )
            return _construct_return_dict(
                textbook,
                prompt_type,
                chapter,
                section,
                subsection,
                prev_chapter_config,
                prompt,
                related_context,
                book_context,
            )

        # Store state for chapter and config
        current_chapter = None
        prev_chapter_config = None

        for counter, elements in enumerate(traverse_textbook_config(config)):
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
                prev_completion = yield step_iterator(
                    textbook,
                    chapter,
                    chapter_config,
                    section,
                    subsection,
                    None,
                    prev_chapter_config,
                    "foreword",
                )

            if chapter != current_chapter:
                # If we are past the foreword, write a chapter summary
                if current_chapter:
                    prev_completion = yield step_iterator(
                        textbook,
                        chapter,
                        chapter_config,
                        section,
                        subsection,
                        prev_completion,
                        prev_chapter_config,
                        "chapter_conclusion",
                    )

                prev_completion = yield step_iterator(
                    textbook,
                    chapter,
                    chapter_config,
                    section,
                    subsection,
                    prev_completion,
                    prev_chapter_config,
                    "chapter_introduction",
                )

                current_chapter = chapter

            prev_completion = yield step_iterator(
                textbook,
                chapter,
                chapter_config,
                section,
                subsection,
                prev_completion,
                prev_chapter_config,
                "chapter_bulk",
            )

            prev_chapter_config = chapter_config

    def construct_prompt(
        self,
        textbook: str,
        chapter: str,
        chapter_config: dict,
        section: str,
        subsection: str,
        prev_completion: Optional[str],
        prev_chapter_config: Optional[dict],
        prompt_type: str,
    ):
        """Construct the prompt for the given chapter and section."""
        self.logger.info(f"Processing {textbook}, Chapter:{chapter}, Summary")
        related_context = (
            with_retry(
                lambda: self.rag_interface.get_contexts(
                    [subsection or section]
                )
            )[0][: self.config.max_related_context_to_sample]
            if self.config.rag_enabled and self.rag_interface
            else TextbookContentGenerator.NO_RAG_TEXT
        )
        book_context = (
            prev_completion[: self.config.max_prev_snippet_to_sample]
            if prev_completion
            else ""
        )

        if prompt_type == "foreword":
            return (
                BOOK_FOREWORD_PROMPT.format(
                    title=textbook,
                    related_context=related_context,
                ),
                related_context,
                book_context,
            )
        elif prompt_type == "chapter_introduction":
            return (
                BOOK_CHAPTER_INTRODUCTION_PROMPT.format(
                    title=textbook,
                    chapter=chapter,
                    related_context=related_context,
                    book_context=book_context,
                    chapter_outline=chapter_config,
                ),
                related_context,
                book_context,
            )
        elif prompt_type == "chapter_bulk":
            return (
                BOOK_CHAPTER_BULK_PROMPT.format(
                    title=textbook,
                    chapter=chapter,
                    section=section,
                    subsection=subsection,
                    related_context=related_context,
                    book_context=book_context,
                ),
                related_context,
                book_context,
            )
        elif prompt_type == "chapter_conclusion":
            return (
                BOOK_CHAPTER_CONCLUSION_PROMPT.format(
                    title=textbook,
                    chapter=chapter,
                    related_context=related_context,
                    book_context=book_context,
                    chapter_outline=prev_chapter_config or "",
                ),
                related_context,
                book_context,
            )
        else:
            raise ValueError(f"Unknown prompt type {prompt_type}")
