"""A module to facilitate seamless construction of input prompts"""
from dataclasses import dataclass


@dataclass
class Prompt:
    """A simple abstraction for building input prompts."""

    expected_inputs: set[str]
    text: str

    def format(self, **kwargs) -> str:
        """Format the prompt into a string"""
        if set(kwargs.keys()) != self.expected_inputs:
            raise ValueError(
                f"Received {kwargs.keys()}, but expected {self.expected_inputs}"
            )
        return self.text.format(**kwargs)


class PromptManager:
    """A manager for available prompts"""

    prompt_modes = {
        "md_instruction": Prompt(
            expected_inputs={"instruction"},
            text="""Below is an instruction that describes a task. Write a response that appropriately completes the request.\n### Instruction:\n{instruction}\n\n### Response:""",
        )
    }

    def __init__() -> None:
        pass

    @staticmethod
    def register_prompt(prompt: Prompt) -> None:
        """Registers the prompt with the prompt manager"""
        PromptManager.prompt_modes[prompt.prompt_mode] = prompt

    @staticmethod
    def get_prompt(prompt_mode: str) -> Prompt:
        """Gets the prompt associated with the specified mode"""
        prompt = PromptManager.prompt_modes.get(prompt_mode)
        if not prompt:
            raise ValueError(
                f"Requested prompt mode {prompt_mode} does not exist!"
            )
        return prompt
