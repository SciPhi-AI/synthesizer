"""A module which facilitates JSONL data writing."""
import json

from sciphi.core.writers.base import DataWriter


class JsonlDataWriter(DataWriter):
    """A class to write data to a JSONL file."""

    def __init__(self, output_path, overwrite=True):
        """Initialize the DataWriter."""
        self.output_path = output_path
        self.overwrite = overwrite

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
