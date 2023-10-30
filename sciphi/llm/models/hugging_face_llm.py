"""A module for managing local HuggingFace models."""

from dataclasses import dataclass, field

from sciphi.core import LLMProviderName
from sciphi.llm.base import LLM, LLMConfig
from sciphi.llm.config_manager import model_config


@model_config
@dataclass
class HuggingFaceConfig(LLMConfig):
    """Configuration for local HuggingFace models."""

    # Base
    provider_name: LLMProviderName = LLMProviderName.HUGGING_FACE
    model_name: str = "gpt2"
    temperature: float = 0.7
    top_p: float = 1.0

    # Generation parameters
    top_k: int = 100
    max_tokens_to_sample: int = 256
    do_sample: bool = True
    num_beams: int = 1

    # Model and Tokenizer extras
    device: str = "cpu"
    add_model_kwargs: dict = field(default_factory=dict)
    add_tokenizer_kwargs: dict = field(default_factory=dict)
    add_generation_kwargs: dict = field(default_factory=dict)


class HuggingFaceLLM(LLM):
    """A concrete class for creating a local HuggingFace model."""

    def __init__(
        self,
        config: HuggingFaceConfig,
    ) -> None:
        try:
            import torch  # noqa: F401
            from transformers import (
                AutoModelForCausalLM,
                AutoTokenizer,
                GenerationConfig,
            )
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
        model_name = self.config.model_name
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            token="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",
            **config.add_model_kwargs,
        ).to(self.config.device)
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            token="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",
            **config.add_tokenizer_kwargs,
        )
        self.generation_config = GenerationConfig.from_pretrained(
            model_name,
            top_k=self.config.top_k,
            top_p=self.config.top_p,
            max_new_tokens=self.config.max_tokens_to_sample,
            do_sample=self.config.do_sample,
            num_beams=self.config.num_beams,
            **config.add_generation_kwargs,
        )

    def get_chat_completion(self, messages: list[dict[str, str]]) -> str:
        """Get a completion from the local HuggingFace model."""
        raise NotImplementedError(
            "Chat completion not yet implemented for HuggingFace."
        )

    def get_instruct_completion(self, instruction: str) -> str:
        """Get an instr. completion from local HuggingFace model."""
        # TODO - Should we set `max_length` here? What about `max_tokens_to_sample`?
        # Should we set the device on inputs or is this handled above? Test on GPU inst.
        inputs = self.tokenizer(
            instruction,
            return_tensors="pt",
        ).to(self.config.device)
        raw_completion = self.model.generate(
            inputs["input_ids"], generation_config=self.generation_config
        )
        return self.tokenizer.batch_decode(raw_completion)[0].replace(
            instruction, ""
        )
