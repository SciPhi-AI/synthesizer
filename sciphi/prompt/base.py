"""A module to facilitate seamless construction of input prompts"""
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Union


class PromptStructure(Enum):
    """How are prompts formatted (e.g. single reply, conversation, ..)"""

    SINGLE = "single"
    CONVERSATION = "conversation"


@dataclass
class Prompt:
    """A simple abstraction for building input prompts."""

    expected_inputs: set[str]
    raw_text: Union[str, List[str]]
    structure: PromptStructure
    _text: Optional[Union[str, List[str]]] = None

    def format(self, **kwargs) -> None:
        """Format the prompt into a string"""
        if set(kwargs.keys()) != self.expected_inputs:
            raise ValueError(
                f"Received {kwargs.keys()}, but expected {self.expected_inputs}"
            )
        if self.structure == PromptStructure.SINGLE:
            self._text = self.raw_text.format(**kwargs)
        else:
            # If not a single response, then text is formatted in a list
            self._text = [ele.format(**kwargs) for ele in self.raw_text]

    @property
    def text(self):
        if not self._text:
            raise ValueError(
                "Format prompt before attempting to access the `text` field."
            )
        return self._text


class PromptManager:
    """A manager for available prompts"""

    prompt_modes = {
        "md_instruction": Prompt(
            expected_inputs={"instruction"},
            raw_text="""Below is an instruction that describes a task. Write a response that appropriately completes the request.\n### Instruction:\n{instruction}\n\n### Response:""",
            structure=PromptStructure.SINGLE,
        ),
        "evol_instruct": Prompt(
            expected_inputs={"method", "question"},
            raw_text="""Please increase the difficulty of the given programming test question a bit.\nYou can increase the difficulty using, but not limited to, the following methods:\n{method}\n\n{question}""",
            structure=PromptStructure.SINGLE,
        ),
    }

    def __init__() -> None:
        pass

    @staticmethod
    def get_prompt(prompt_mode: str) -> Prompt:
        """
        Gets the list of prompts associated with the specified mode
        """
        prompt = PromptManager.prompt_modes.get(prompt_mode)
        if not prompt:
            raise ValueError(
                f"Requested prompt mode {prompt_mode} does not exist!"
            )
        return prompt
