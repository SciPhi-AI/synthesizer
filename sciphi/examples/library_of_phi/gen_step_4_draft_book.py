# type: ignore
import os
from typing import Generator, Tuple

import fire
import requests
from requests.auth import HTTPBasicAuth

from sciphi.interface import InterfaceManager, ProviderName
from sciphi.llm import LLMConfigManager
from sciphi.writers import RawDataWriter


def get_key(config_dict: dict) -> str:
    """Get the key from a dictionary with a single key-value pair"""
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


class TextbookContentGenerator:
    """Generates textbook content from parsed course data."""

    def __init__(
        self,
        provider="openai",
        model="gpt-3.5-turbo-instruct",
        parsed_dir="raw_data",
        toc_dir="output_step_3",
        output_dir="output_step_4",
        textbook="field_computer_science_subfield_artificial_intelligence_course_name_Introduction_to_Deep_Learning",
    ):
        self.provider = provider
        self.model = model
        self.parsed_dir = parsed_dir
        self.toc_dir = toc_dir
        self.output_dir = output_dir
        self.textbook = textbook

        self.url = os.environ["WIKI_SERVER_URL"]
        self.username = os.environ["WIKI_SERVER_USERNAME"]
        self.password = os.environ["WIKI_SERVER_PASSWORD"]

        # Constants for sampling
        self.related_context_to_sample = 2_000
        self.prev_snippet_to_sample = 2_000

    def wiki_search_api(
        url: str, username: str, password: str, query: str
    ) -> dict:
        """
        Queries the search API with the provided credentials and query.
        The expected output is a JSON response containing matches.
        The API used in generating the initially shared textbook samples
        contains
        """
        # Make the GET request with basic authentication and the query parameter
        response = requests.get(
            url,
            auth=HTTPBasicAuth(username, password),
            params={"query": query, "k": 10},
        )

        # Check if the request was successful
        if response.status_code == 200:
            return response.json()["match"]  # Return the JSON response
        else:
            response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code

    def run(self):
        local_pwd = os.path.dirname(os.path.realpath(__file__))
        yml_file_path = os.path.join(
            local_pwd, self.parsed_dir, self.toc_dir, f"{self.textbook}.yaml"
        )
        yml_config = self.load_yaml_file(yml_file_path, do_prep=True)

        # Build an LLM and provider interface
        provider_name = ProviderName(self.provider)
        llm_config = LLMConfigManager.get_config_for_provider(
            provider_name
        ).create(max_tokens_to_sample=None)
        llm_provider = InterfaceManager.get_provider(
            self.provider, self.model, llm_config
        )

        # Create an instance of the generator
        traversal_generator = traverse_config(yml_config)

        output_path = os.path.join(
            local_pwd, parsed_dir, output_dir, f"{textbook}.md"
        )
        writer = RawDataWriter(output_path)

        current_chapter = None
        chapter_chunks = ""
        prev_chapter_config = None
        is_new_chapter = False
        for counter, elements in enumerate(traversal_generator):
            # elements is a tuple containing the names of textbook, chapter, section, and subsection.
            textbook, chapter, section, subsection, chapter_config = elements
            # Build the forward prompt
            if counter == 0:
                related_context = wiki_search_api(
                    url, username, password, textbook
                )
                foreward_prompt = FOREWARD_PROMPT.format(
                    title=textbook,
                    related_context=related_context[
                        :related_context_to_sample
                    ],
                )
                foreward = llm_provider.get_completion(foreward_prompt)
                prev_response = foreward
                writer.write(f"{prev_response}\n")
                print(f"Foreward Completion:\n{prev_response}\n\n")

            # Build the capter conclusion
            if chapter != current_chapter:
                # Summarize the previous chapter
                if current_chapter != None:
                    chapter_summary_prompt = CHAPTER_SUMMARY_PROMPT.format(
                        title=textbook,
                        chapter=current_chapter,
                        book_context=f"Chapter outline:\n{str(prev_chapter_config)}\n\nChapter Introduction:{chapter_intro_prompt}\n\nSome Chapter Chunks:\n{chapter_chunks[0:4_000]}",
                    )
                    chapter_completion = llm_provider.get_completion(
                        chapter_summary_prompt
                    )

                    chapter_chunks = ""
                    current_chapter = chapter
                    prev_response = chapter_completion
                    writer.write(f"{prev_response}\n")
                    print(f"Chapter Conclusion:\n{prev_response}\n\n")

                # Introduce the new chapter
                chapter_intro_prompt = CHAPTER_INTRODUCTION_PROMPT.format(
                    title=textbook,
                    chapter=chapter,
                    book_context=str(chapter_config),
                )
                chapter_introduction = llm_provider.get_completion(
                    chapter_intro_prompt
                )
                prev_response = chapter_introduction
                writer.write(f"{prev_response}\n")
                print(f"Chapter Introduction:\n{prev_response}\n\n")
                current_chapter = chapter

            related_context = search_api(
                url, username, password, subsection or section
            )

            step_prompt = CHUNK_PROMPT.format(
                title=textbook,
                chapter=chapter,
                section=section,
                subsection=subsection or "",
                related_context=related_context[:related_context_to_sample],
                book_context=prev_response[:prev_snippet_to_sample],
            )

            step_completion = llm_provider.get_completion(step_prompt)
            chapter_chunks += f"\n# {step_completion[:500]}"
            prev_response = step_completion
            writer.write(f"{step_completion}\n")
            print(f"{counter} Completion:\n{step_completion}\n\n")


if __name__ == "__main__":
    fire.Fire(TextbookContentGenerator)
