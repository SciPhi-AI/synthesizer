"""
KA Course Data Scraper

Description:
    This script is designed to scrape course data from the OpenCourseWare (KA) website.
    It extracts details like course number, title, URL, resource level, page contents, and more.

Usage:
    Command-line interface:
        $ poetry run python sciphi/examples/library_of_phi/raw_data/ka_scraper.py scrape \
            --input_file_name=ka_topics.html \
            --output_file_name=scraped_ka.jsonl \
            --sleep_time=1 \
            --log_level=INFO

Parameters:
    data_directory (Optional[str], default=None): 
        Path to the directory where the input file is located 
        and where the output file will be saved. 
        If not specified, defaults to the directory of this script.

    input_file_name (str, default="ka_topics.html"): 
        Name of the input HTML file containing KA course listings.
    
    output_file_name (str, default="ka_scraped.jsonl"): 
        Name of the output JSONL file where scraped data will be saved.
        
    sleep_time (int, default=0): 
        Time (in seconds) to pause between scraping consecutive courses.
    
    log_level (str, default="INFO"): 
        Logging level for the scraper. Can be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL.
"""
import logging
import os
import re
import time
from typing import Dict, List, Optional, Union

import fire
import requests
from bs4 import BeautifulSoup

from sciphi.writers import JsonlDataWriter

# Constants
BASE_URL = "https://www.khanacademy.org"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)
HEADERS = {"User-Agent": USER_AGENT}
PAGE_TYPES = [
    "syllabus",
]

logging.basicConfig(level=logging.INFO)


class Scraper:
    """Scraper for KA course data."""

    def __init__(self, sleep_time: int = 0, log_level: str = "INFO"):
        self.sleep_time = sleep_time
        logging.basicConfig(level=getattr(logging, log_level.upper()))

    def scrape(
        self,
        data_directory: Optional[str] = None,
        input_file_name: str = "ka_courses.html",
        output_file_name: str = "ka_scraped.jsonl",
    ):
        """Scrape course data from KA and save to an output file."""

        if not data_directory:
            data_directory = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.join(data_directory, input_file_name)) as f_open:
            html_content = f_open.read()

        soup = BeautifulSoup(html_content, "html.parser")

        # Find all the 'a' tags with 'href' attributes
        courses = soup.find_all("a", href=True)

        # Extract and print the href values and corresponding text
        for a_tag in courses:
            href = a_tag["href"]
            text = a_tag.text.strip()  # Remove leading/trailing whitespace
            print(f"Text: {text}, Href: {href}")

        writer = JsonlDataWriter(
            os.path.join(data_directory, output_file_name)
        )

        for course in courses:
            course_data = Scraper.extract_course_data(course)
            writer.write([course_data])
            time.sleep(self.sleep_time)

    @staticmethod
    def get_soup(page_url: str) -> Optional[BeautifulSoup]:
        """Retrieve and parse a webpage."""
        try:
            response = requests.get(page_url, headers=HEADERS)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            logging.error(f"Failed to retrieve {page_url}. Error: {e}")
            return None

    @staticmethod
    def read_page(
        page_url: str,
    ) -> Dict[str, Union[str, List[Dict[str, str]]]]:
        """Read the given page URL and return a dictionary of the extracted data."""
        logging.info(f"Scraping {page_url}")

        ka_link = f"{BASE_URL}{page_url.rstrip('/')}" if page_url else None
        soup = Scraper.get_soup(ka_link)

        units = soup.find_all("a")
        result = {}

        for unit in units:
            if page_url in unit["href"] and "/v/" in unit["href"]:
                print(f'{page_url}\n\t{unit["href"]} {unit.text.strip()}')

            # logging.debug("Scraping the syllabus")
            # try:
            #     result["topics"] = Scraper._get_topics_and_depths(soup)
            # except Exception as e:
            #     logging.warning(f"Failed to extract topics. Error: {e}")
            #     result["topics"] = {}

        return result

    @staticmethod
    def _extract_text(
        element: BeautifulSoup, tag: str, class_: str
    ) -> Optional[str]:
        """Extract text from an element with a specific tag and class."""
        found_element = element.find(tag, class_=class_)
        return found_element.get_text(strip=True) if found_element else None

    def _extract_leading_text(soup: BeautifulSoup) -> str:
        """Extract leading text from the soup."""
        main_section = soup.find("main", id="course-content-section")
        if main_section:
            paragraphs = main_section.find_all("p")
            leading_text = " ".join(
                paragraph.get_text(strip=True) for paragraph in paragraphs
            )
            return Scraper._clean_text(leading_text)
        return ""

    def extract_course_data(
        course: BeautifulSoup,
    ) -> Dict[str, Union[str, List[Dict[str, str]]]]:
        """Extract course data from an article tag."""
        logging.debug("Extracting course data...")

        course_title = course.text.strip()
        course_url = course["href"]

        course_data = {
            "course_title": course_title,
            "course_url": course_url,
            "page_contents": {},
        }

        # Only scrape the syllabus page for now
        for page_type in PAGE_TYPES:
            try:
                course_data["page_contents"][page_type] = Scraper.read_page(
                    course_url
                )
            except requests.RequestException:
                pass

        return course_data

        return course_data

    @staticmethod
    def _extract_table_rows(soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract table rows from the soup."""
        logging.debug("Extracting table rows...")

        rows = soup.find_all("tr")
        table_data = []

        for row in rows:
            try:
                note_number = Scraper._clean_text(
                    row.find_all("td")[0].get_text(strip=True)
                )
                topic_col = row.find_all("td")[1]
                topic = Scraper._clean_text(
                    topic_col.get_text(strip=True).split("(")[0].strip()
                )
                link = topic_col.find("a")
                note_url = link["href"] if link else None
                table_data.append(
                    {
                        "note_number": note_number,
                        "topic": topic,
                        "note_url": note_url,
                    }
                )
            except IndexError:
                logging.debug(
                    "Skipping row that doesn't match the expected format"
                )
                pass  # Skip rows that don't match the expected format

        return table_data

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean the given text."""
        text = text.replace("\xa0", " ")
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _get_topics_and_depths(soup: BeautifulSoup) -> Dict[str, int]:
        """Extract topics and their depths from the soup."""
        topics = soup.select("span.topic-text-wrapper > a.course-info-topic")
        return {
            topic.get_text(strip=True): len(
                topic.find_parent("li").find_parents("ul")
            )
            - 1
            for topic in topics
        }


def main():
    """Main function."""
    fire.Fire(Scraper)


if __name__ == "__main__":
    main()
