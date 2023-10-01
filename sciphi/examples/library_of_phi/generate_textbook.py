# type: ignore
"""
YAML Table of Contents to Textbook Generator

WARNING - This script is very rough and needs significant enhancements to fully productionize
Description:
    This script processes YAML files and generates a detailed Table of Contents for a new textbook accompanying the course.

Usage:
    Command-line interface:
        $ python sciphi/examples/library_of_phi/generate_textbook.py run
Parameters:
    provider (str): 
        The provider to use. Default is 'openai'.
    model (str): 
        The model name to use. Default is 'gpt-3.5-turbo-instruct'.
    parsed_dir (str): 
        Directory containing parsed data. Default is 'raw_data'.
    toc_dir (str): 
        Directory for the table of contents. Default is 'table_of_contents'.
    output_dir (str): 
        Directory for the output. Default is 'output_step_4'.
      (str): 
        Name of the textbook. Default is 'Introduction_to_Deep_Learning'.
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
import fire

from sciphi.examples.library_of_phi.gen_step_4_draft_book import (
    TextbookContentGenerator,
)


class TextbookContentGeneratorSimplified:
    def __init__(self) -> None:
        pass

    def run(
        self,
        provider="openai",
        model="gpt-4-0613",
        parsed_dir="raw_data",
        toc_dir="table_of_contents",
        output_dir="created_textbooks",
        textbook="Introduction_to_Deep_Learning",
        max_related_context_to_sample=2_000,
        max_prev_snippet_to_sample=2_000,
        do_wiki=True,
        wiki_server_url=None,
        wiki_username=None,
        wiki_password=None,
        log_level="INFO",
    ):
        """Runs the generation process to create a textbook from the YAML table of contents."""
        TextbookContentGenerator(
            provider,
            model,
            parsed_dir,
            toc_dir,
            output_dir,
            textbook,
            max_related_context_to_sample,
            max_prev_snippet_to_sample,
            do_wiki,
            wiki_server_url,
            wiki_username,
            wiki_password,
            log_level,
        ).run()


if __name__ == "__main__":
    fire.Fire(TextbookContentGeneratorSimplified)
