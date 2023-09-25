"""A module which defines the abstract bata class for data writers."""
import os
import time
from abc import ABC, abstractmethod


class DataWriter(ABC):
    """An abstract class for data writers."""

    def __init__(self, output_path):
        self.output_path = output_path

    def _get_modified_path(self):
        """Modify the output path if the file already exists and overwriting is not allowed."""
        if not self.overwrite and os.path.exists(self.output_path):
            base_name, ext = os.path.splitext(self.output_path)
            return f"{base_name}_{int(time.time())}{ext}"
        return self.output_path

    @abstractmethod
    def write(self, data):
        """Write data to the specified path."""
        pass
