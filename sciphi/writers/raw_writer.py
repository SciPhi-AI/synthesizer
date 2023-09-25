"""A module which facilitates raw data writing."""
from sciphi.writers.base import DataWriter


class RawDataWriter(DataWriter):
    """A class to write raw data file."""

    def __init__(self, output_path, overwrite=True):
        """Initialize the DataWriter."""
        self.output_path = output_path
        self.overwrite = overwrite

    def write(self, data: str) -> None:
        """
        Write the provided data to the specified path.

        Args:
            data (list): List of data entries to be written.
        """
        path = self._get_modified_path()

        with open(path, "a") as f:
            f.write(data + "\n")
