"""A module to facilitate seamless construction of input prompts"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union


class PromptStructure(Enum):
    """How are prompts formatted (e.g. single reply, conversation, ..)"""

    SINGLE = "single"
    CONVERSATION = "conversation"


@dataclass
class Prompt:
    """A simple abstraction for building input prompts."""

    expected_inputs: set[str]
    raw_text: Union[str, list[str]]
    structure: PromptStructure
    _text: Optional[Union[str, list[str]]] = None

    def format(self, **kwargs) -> None:
        """Format the prompt into a string"""
        if set(kwargs.keys()) != self.expected_inputs:
            raise ValueError(
                f"Received {kwargs.keys()}, but expected {self.expected_inputs}"
            )
        if self.structure == PromptStructure.SINGLE:
            if not isinstance(self.raw_text, str):
                raise ValueError(
                    f"Expected `raw_text` to be a string, but got {type(self.raw_text)}"
                )
            self._text = self.raw_text.format(**kwargs)
        else:
            if not isinstance(self.raw_text, list) and all(
                isinstance(item, str) for item in self.raw_text
            ):
                raise ValueError(
                    f"Expected `raw_text` to be a list of strings, but got {type(self.raw_text)}"
                )
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

    stock_prompts = {
        "md_instruction": Prompt(
            expected_inputs={"instruction"},
            raw_text="""Below is an instruction that describes a task. Write a response that appropriately completes the request.\n### Instruction:\n{instruction}\n\n### Response:""",
            structure=PromptStructure.SINGLE,
        ),
        "unit": Prompt(
            expected_inputs={"instruction"},
            raw_text="""{instruction}""",
            structure=PromptStructure.SINGLE,
        ),
    }

    def __init__(self, stock_prompts=stock_prompts) -> None:
        self.stock_prompts = stock_prompts

    def get_prompt(self, selected_prompt: str) -> Prompt:
        """
        Gets the list of prompts associated with the specified mode
        """
        prompt = self.stock_prompts.get(selected_prompt)
        if not prompt:
            raise ValueError(
                f"Requested prompt mode {selected_prompt} does not exist!"
            )
        return prompt
