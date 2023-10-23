"""Managers textbook generation configs"""
import collections
import glob
import logging
import os
from typing import Any, Generator, Optional, Tuple

import yaml
from tqdm import tqdm

from sciphi.core.utils import SciPhiConfig, get_config_dir
from sciphi.library_of_phi.helpers import load_yaml_file


def traverse_textbook_config(
    config: dict,
) -> Generator[Tuple[str, str, str, str, dict], None, None]:
    """
    Traverse the config and yield textbook,
    chapter, section, subsection names, and full chapter config
    """

    def get_key(config_dict: dict) -> str:
        """Get the key from a dictionary with a single key-value pair"""
        if not config_dict:
            raise KeyError("Dictionary is empty, no key found")
        return next(iter(config_dict))

    textbook_name = get_key(config["textbook"])
    if not textbook_name:
        raise KeyError("No textbook name found in config")
    chapters = config["textbook"][textbook_name]["chapters"]
    if not chapters:
        raise KeyError("No chapters found in config")

    for chapter in chapters:
        chapter_name = get_key(chapter)
        sections = chapter[chapter_name]["sections"]

        for section in sections:
            if isinstance(section, str):
                yield textbook_name, chapter_name, section, "", chapter[
                    chapter_name
                ]
                continue

            section_name = get_key(section)
            subsections = section[section_name].get("subsections", [])

            if not subsections:
                yield textbook_name, chapter_name, section_name, "", chapter[
                    chapter_name
                ]
                continue

            for subsection in subsections:
                if isinstance(subsection, str):
                    yield textbook_name, chapter_name, section_name, subsection, chapter[
                        chapter_name
                    ]
                else:
                    subsection_name = get_key(subsection)
                    yield textbook_name, chapter_name, section_name, subsection_name, chapter[
                        chapter_name
                    ]


class ConfigurationManager:
    """Manages the configuration for textbook generation."""

    DEFAULT_SETTINGS_CONFIG = "book_draft_settings.yml"

    def __init__(self, config_path: Optional[str] = None) -> None:
        self.config_path = config_path or os.path.join(
            get_config_dir(),
            "generation_settings",
            ConfigurationManager.DEFAULT_SETTINGS_CONFIG,
        )
        self.load_config()

    def load_config(self) -> Any:
        """Load the configuration."""
        # Load the configuration
        with open(
            self.config_path,
            "r",
        ) as file:
            # TODO - Find a less hacky solution than any typing
            config: Any = SciPhiConfig(yaml.safe_load(file))
        self.config = config
        return config

    def validate_config(self, logger: logging.Logger) -> None:
        """Validate the configuration."""
        if not self.config:
            raise ValueError("No configuration loaded.")
        # Check RAG configurations
        if self.config.rag_enabled and not all(
            [
                self.config.rag_api_base,
                self.config.rag_api_key,
            ]
        ):
            raise ValueError(
                "RAG self.configuration is invalid. Make sure you provide a RAG server base and token."
            )

        # Check for YAML file paths
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

        if not yml_file_paths:
            raise ValueError("No YAML files found in the specified directory.")

        # Check the output path
        output_dir = os.path.join(self.config.data_dir, self.config.output_dir)
        if not os.path.exists(os.path.dirname(output_dir)):
            os.makedirs(os.path.dirname(output_dir))

        # Output some summary statistics
        summary = collections.OrderedDict()
        summary["RAG Server URL"] = self.config.rag_api_base
        summary["LLM Provider"] = self.config.llm_provider_name
        summary["LLM Model Name"] = self.config.llm_model_name
        summary["Total YAML Files"] = len(yml_file_paths)
        summary["Output Directory"] = os.path.dirname(output_dir)

        failed_loads = 0
        logger.info("Validating configs now...")
        for yml in tqdm(yml_file_paths):
            try:
                yml_config = load_yaml_file(yml)
                # check that we can traverse the config
                _ = [ele for ele in traverse_textbook_config(yml_config)]
            except Exception as e:
                logger.error(f"Failed to load {yml} with error: {e}")
                failed_loads += 1

        summary["YAML Files with Errors"] = failed_loads
        summary["YAML Failure Rate"] = float(failed_loads) / len(
            yml_file_paths
        )

        logger.info("\nDry Run Summary:")
        for key, value in summary.items():
            logger.info(f"{key}: {value}")

    def get_yml_file_paths(self, logger: logging.Logger) -> list:
        """Get the YAML file paths."""
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
            yml_file_paths += glob.glob(
                os.path.join(
                    self.config.data_dir, self.config.toc_dir, "**/**/*.yaml"
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
                if not self._book_exists(yml_file_path):
                    filtered_books.append(yml_file_path)
                else:
                    logger.warning(
                        f"Skipping {yml_file_path} as it already exists."
                    )
            yml_file_paths_chunk = filtered_books
        return yml_file_paths_chunk

    def _book_exists(self, yml_path: str) -> bool:
        """Check if the book for the given YAML file exists in the output directory."""
        book_name = os.path.splitext(os.path.basename(yml_path))[0]

        # Assume the book files in the output directory have the ".md" extension
        output_path = os.path.join(
            self.config.data_dir, self.config.output_dir, f"{book_name}.md"
        )
        return os.path.exists(output_path)
