"""Generates textbook content from parsed course data."""
import fire

from sciphi.synthetic_data import TextbookContentGenerator

if __name__ == "__main__":
    fire.Fire(TextbookContentGenerator)
