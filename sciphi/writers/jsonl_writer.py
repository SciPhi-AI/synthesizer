"""A module which facilitates JSONL data writing."""
import json
import os
import time

from sciphi.writers.base import DataWriter


class JsonlDataWriter(DataWriter):
    """A class to write data to a JSONL file."""

    def __init__(self, output_path, overwrite=True):
        """
        Initialize the DataWriter.

        Args:
            output_path (str): The initial path where the data should be written.
            overwrite (bool): If true, overwrite the file if it exists. Otherwise, add a timestamp.
            structured_format (bool): If true, writes the data in a structured format (e.g., JSON).
        """
        self.output_path = output_path
        self.overwrite = overwrite

    def _get_modified_path(self):
        """Modify the output path if the file already exists and overwriting is not allowed."""
        if not self.overwrite and os.path.exists(self.output_path):
            base_name, ext = os.path.splitext(self.output_path)
            return f"{base_name}_{int(time.time())}{ext}"
        return self.output_path

    def write(self, data: list[dict]) -> None:
        """
        Write the provided data to the specified path.

        Args:
            data (list): List of data entries to be written.
        """
        path = self._get_modified_path()

        with open(path, "a") as f:
            for entry in data:
                f.write(json.dumps(entry) + "\n")
