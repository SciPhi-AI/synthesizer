import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class Evaluator(ABC):
    """Evaluator base class."""

    NAME: str = "Evaluator"

    @abstractmethod
    def initialize_prompts(self) -> None:
        pass

    @abstractmethod
    def build_prompt(self, entry: dict, context: str) -> str:
        pass

    @abstractmethod
    def evaluate_response(self, response: str, index: int) -> bool:
        pass

    @abstractmethod
    def get_cleaned_response(self, response: str) -> str:
        pass
