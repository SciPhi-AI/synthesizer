"""A module for managing local HuggingFace models."""

from dataclasses import dataclass, field

from sciphi.core import LLMProviderName
from sciphi.llm import LLM, GenerationConfig, LLMConfig
from sciphi.llm.config_manager import model_config

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from transformers import GenerationConfig as HFGenerationConfig


@model_config
@dataclass
class HuggingFaceConfig(LLMConfig):
    """Configuration for local HuggingFace models."""

    # Base
    provider_name: LLMProviderName = LLMProviderName.HUGGING_FACE
    model_name: str = "gpt2"
    temperature: float = 0.7
    # Model and Tokenizer extras
    device: str = "cpu"


class HuggingFaceLLM(LLM):
    """A concrete class for creating a local HuggingFace model."""

    def __init__(
        self,
        config: HuggingFaceConfig,
    ) -> None:
        try:
            import torch  # noqa: F401
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError:
            raise ImportError(
                "Please install the torch and transformers packages before attempting to run with a HuggingFace model. This can be accomplished via `pip install transformers`."
            )

        super().__init__(
            config,
        )
        # Set the config here, again, for typing purposes
        # TODO - Can setting the config twice be avoided?
        if not isinstance(self.config, HuggingFaceConfig):
            raise ValueError(
                "The provided config must be an instance of HuggingFaceConfig."
            )
        self.config: HuggingFaceConfig = config

        # Create the model, tokenizer, and generation config
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            **config.add_model_kwargs,
        ).to(self.config.device)
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.model_name,
            **config.add_tokenizer_kwargs,
        )

    def get_chat_completion(
        self,
        messages: list[dict[str, str]],
        generation_config: GenerationConfig,
    ) -> str:
        """Get a completion from the local HuggingFace model."""
        raise NotImplementedError(
            "Chat completion not yet implemented for HuggingFace."
        )

    def get_instruct_completion(
        self, instruction: str, generation_config: GenerationConfig
    ) -> str:
        """Get an instr. completion from local HuggingFace model."""
        # TODO - Should we set `max_length` here? What about `max_tokens_to_sample`?
        # Should we set the device on inputs or is this handled above? Test on GPU inst.
        inputs = self.tokenizer(
            instruction,
            return_tensors="pt",
        ).to(self.config.device)
        raw_completion = self.model.generate(
            inputs["input_ids"],
            generation_config=self._get_hf_generation_config(
                generation_config
            ),
        )
        return self.tokenizer.batch_decode(raw_completion)[0].replace(
            instruction, ""
        )

    def _get_hf_generation_config(
        self, generation_config: GenerationConfig
    ) -> "HFGenerationConfig":
        """Get the generation config for this model."""
        return GenerationConfig.from_pretrained(
            self.config.model_name,
            top_k=generation_config.top_k,
            top_p=generation_config.top_p,
            max_new_tokens=generation_config.max_tokens_to_sample,
            do_sample=generation_config.do_sample,
            num_beams=generation_config.num_beams,
            **generation_config.add_generation_kwargs,
        )
