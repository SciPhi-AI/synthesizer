"""A module which defines the abstract bata class for data writers."""
from abc import ABC, abstractmethod


class DataWriter(ABC):
    """An abstract class for data writers."""

    def __init__(self, output_path):
        self.output_path = output_path

    @abstractmethod
    def write(self, data):
        """Write data to the specified path."""
        pass
