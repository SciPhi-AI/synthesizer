"""A module for creating HuggingFace models."""

from dataclasses import dataclass, field

from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig

from sci_phi.core import ProviderName
from sci_phi.llm.base import LLM, LLMConfig
from sci_phi.llm.config_manager import model_config


@model_config
@dataclass
class HuggingFaceConfig(LLMConfig):
    """Configuration for HuggingFace models."""

    # Base
    provider_name: ProviderName = ProviderName.HUGGING_FACE
    model_name: str = "gpt-2"
    version: str = "0.1.0"
    temperature: float = 0.7
    top_p: float = 1.0

    # Generation parameters
    top_k: float = 100.0
    max_tokens_to_sample: int = 256
    do_sample: bool = False
    num_beams: int = 1

    # Model and Tokenizer extras
    device: str = "auto"
    add_model_kwargs: dict = field(default_factory=dict)
    add_tokenizer_kwargs: dict = field(default_factory=dict)
    add_generation_kwargs: dict = field(default_factory=dict)


class HuggingFaceLLM(LLM):
    """A concrete class for creating HuggingFace models."""

    def __init__(
        self,
        config: HuggingFaceConfig,
    ) -> None:
        super().__init__(
            config,
        )
        model_name = self.config.model_name
        # TODO - Move offload_folder upstream?
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map=self.config.device,
            trust_remote_code=True,
            **config.add_model_kwargs,
            offload_folder="temp/",
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            device_map=self.config.device,
            **config.add_tokenizer_kwargs,
        )
        self.generation_config = GenerationConfig.from_pretrained(
            model_name,
            top_k=self.config.top_k,
            top_p=self.config.top_p,
            max_tokens_to_sample=self.config.max_tokens_to_sample,
            do_sample=self.config.do_sample,
            num_beams=self.config.num_beams,
            **config.add_generation_kwargs,
        )

    def get_completion(self, prompt: str) -> str:
        """Get a completion from the OpenAI API based on the provided messages."""
        # TODO - Should we set `max_length` here? What about `max_tokens_to_sample`?
        # Should we set the device on inputs or is this handled above? Test on GPU inst.
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
        ).to(self.config.device)
        raw_completion = self.model.generate(inputs["input_ids"])
        return [
            ele.replace(prompt, "")
            for ele in self.tokenizer.batch_decode(raw_completion)
        ]
