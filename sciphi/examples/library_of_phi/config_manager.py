"""Managers textbook generation configs"""
import collections
import glob
import logging
import os

import yaml
from tqdm import tqdm

from sciphi.core.utils import SciPhiConfig, get_config_dir
from sciphi.examples.helpers import load_yaml_file, traverse_config


class ConfigurationManager:
    """Manages the configuration for textbook generation."""

    DEFAULT_SETTINGS_CONFIG = "book_draft_settings.yml"

    def __init__(self, config_path: str = None) -> None:
        self.config_path = config_path or os.path.join(
            get_config_dir(),
            "generation_settings",
            ConfigurationManager.DEFAULT_SETTINGS_CONFIG,
        )
        pass

    def load_config(self) -> SciPhiConfig:
        """Load the configuration."""
        # Load the configuration
        with open(
            self.config_path,
            "r",
        ) as file:
            config = SciPhiConfig(yaml.safe_load(file))
        self.config = config
        return config

    def validate_config(self, logger: logging.Logger) -> None:
        """Validate the configuration."""
        if not self.config:
            raise ValueError("No configuration loaded.")
        # Check RAG configurations
        if self.config.do_rag and not all(
            [
                self.config.rag_url,
                self.config.rag_username,
                self.config.rag_password,
            ]
        ):
            raise ValueError(
                "RAG self.configuration is invalid. Make sure you provide a RAG server rag_url, rag_username, and rag_password."
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
        output_path = os.path.join(
            self.config.data_dir, self.config.output_dir, "dry_run_output"
        )
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))

        # Output some summary statistics
        summary = collections.OrderedDict()
        summary["RAG Server URL"] = self.config.rag_url
        summary["LLM Provider"] = self.config.llm_provider
        summary["LLM Model Name"] = self.config.llm_model_name
        summary["Total YAML Files"] = len(yml_file_paths)
        summary["Output Directory"] = os.path.dirname(output_path)

        failed_loads = 0
        logger.info("Validating configs now...")
        for yml in tqdm(yml_file_paths):
            try:
                yml_config = load_yaml_file(yml)
                # check that we can traverse the config
                _ = [ele for ele in traverse_config(yml_config)]
            except:
                failed_loads += 1

        summary["YAML Files with Errors"] = failed_loads
        summary["YAML Failure Rate"] = float(failed_loads) / len(
            yml_file_paths
        )

        logger.info("\nDry Run Summary:")
        for key, value in summary.items():
            logger.info(f"{key}: {value}")

    def get_yml_file_paths(self) -> list:
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
                    self.logger.warning(
                        f"Skipping {yml_file_path} as it already exists."
                    )
            yml_file_paths_chunk = filtered_books
        return yml_file_paths_chunk
