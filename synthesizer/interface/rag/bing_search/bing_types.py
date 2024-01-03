from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class ImageInfo(BaseModel):
    thumbnailUrl: HttpUrl
    hostPageUrl: HttpUrl
    width: int
    height: int
    sourceWidth: int
    sourceHeight: int


class Entity(BaseModel):
    id: HttpUrl
    webSearchUrl: HttpUrl
    name: str
    url: Optional[HttpUrl] = None
    description: str
    bingId: Optional[str] = None
    image: Optional[ImageInfo] = None


class DeepLink(BaseModel):
    name: str
    url: HttpUrl
    snippet: Optional[str] = ""


class WebPage(BaseModel):
    id: HttpUrl
    name: str
    url: HttpUrl
    isFamilyFriendly: bool
    displayUrl: str
    snippet: str
    dateLastCrawled: datetime
    language: str
    isNavigational: bool
    deepLinks: Optional[List[DeepLink]] = []


class Publisher(BaseModel):
    name: str


class Creator(BaseModel):
    name: str


class Video(BaseModel):
    webSearchUrl: HttpUrl
    name: str
    description: str
    thumbnail: ImageInfo  # Replacing individual image fields with ImageInfo
    datePublished: datetime
    publisher: List[Publisher]
    creator: Optional[Creator]
    contentUrl: HttpUrl
    hostPageUrl: HttpUrl
    encodingFormat: str
    hostPageDisplayUrl: HttpUrl
    duration: Optional[str]
    viewCount: Optional[int]


class DisplayConfig(BaseModel):
    show_entities: bool = True
    show_related_queries: bool = True
    show_web_pages: bool = True
    show_videos: bool = True

    # Add more specific configurations as needed, for example:
    entity_fields: List[str] = ["name", "url", "description"]
    web_page_fields: List[str] = ["name", "url", "snippet"]
    video_fields: List[str] = ["name", "description", "contentUrl"]


class SearchResult(BaseModel):
    """A dataclass to store the search result"""

    url: str
    title: str
    dataset: str
    metadata: str
    text: str

    def __init__(self, **data):
        super().__init__(**data)
        if self.title and self.title == self.text[0 : len(self.title)]:
            self.text = self.text[len(self.title) :]
        self.text = self.text.strip()

    def to_string_dict(self) -> dict:
        """Returns a dictionary representation with all values as strings."""
        return {
            "url": self.url,
            "title": self.title,
            "dataset": self.dataset,
            "metadata": self.metadata,
            "text": self.text,
        }
