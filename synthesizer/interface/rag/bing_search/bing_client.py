from typing import Any, Dict, List

import requests

from .bing_types import (
    Creator,
    DisplayConfig,
    Entity,
    ImageInfo,
    Publisher,
    SearchResult,
    Video,
    WebPage,
)


class BingSearchClient:
    FIELD_NAME_MAPPING = {
        "name": "Title",
        "description": "Snippet",
        "snippet": "Snippet",
        "url": "URL",
        "contentUrl": "URL",
    }

    def __init__(self, subscription_key: str):
        self.subscription_key = subscription_key
        self.search_url = "https://api.bing.microsoft.com/v7.0/search"
        self.headers = {"Ocp-Apim-Subscription-Key": self.subscription_key}

    def search(self, query: str, count: int = 30) -> Dict[str, Any]:
        params = {
            "q": query,
            "textDecorations": True,
            "textFormat": "HTML",
            "count": count,
        }
        response = requests.get(
            self.search_url, headers=self.headers, params=params
        )
        response.raise_for_status()
        search_results = response.json()

        # Parse all types of data
        parsed_data = {
            "entities": self.parse_entities(
                search_results.get("entities", {})
            ),
            "related_queries": self.parse_related_queries(
                search_results.get("relatedSearches", {})
            ),
            "web_pages": self.parse_web_pages(
                search_results.get("webPages", {})
            ),
            "videos": self.parse_videos(search_results.get("videos", {})),
        }

        return parsed_data

    def parse_entities(self, entities_data: Dict[str, Any]) -> List[Entity]:
        entities = entities_data.get("value", [])
        return [Entity.construct(**entity) for entity in entities]

    def parse_related_queries(
        self, related_queries_data: Dict[str, Any]
    ) -> List[str]:
        queries = related_queries_data.get("value", [])
        return [query.get("text", "N/A") for query in queries]

    def parse_web_pages(self, web_pages_data: Dict[str, Any]) -> List[WebPage]:
        web_pages = web_pages_data.get("value", [])
        return [WebPage.construct(**web_page) for web_page in web_pages]

    def parse_videos(self, videos_data: Dict[str, Any]) -> List[Video]:
        videos = videos_data.get("value", [])
        return [
            Video.construct(
                webSearchUrl=video["webSearchUrl"],
                name=video["name"],
                description=video["description"],
                thumbnail=ImageInfo(
                    thumbnailUrl=video["thumbnailUrl"],
                    hostPageUrl=video["hostPageUrl"],
                    width=video["width"],
                    height=video["height"],
                    sourceWidth=video.get(
                        "sourceWidth", video["width"]
                    ),  # Assuming sourceWidth is same as width if not provided
                    sourceHeight=video.get(
                        "sourceHeight", video["height"]
                    ),  # Assuming sourceHeight is same as height if not provided
                ),
                datePublished=video["datePublished"],
                publisher=[
                    Publisher(name=p["name"]) for p in video["publisher"]
                ],
                creator=Creator(name=video["creator"]["name"])
                if video.get("creator")
                else None,
                contentUrl=video["contentUrl"],
                hostPageUrl=video["hostPageUrl"],
                encodingFormat=video["encodingFormat"],
                hostPageDisplayUrl=video["hostPageDisplayUrl"],
                duration=video.get("duration"),
                viewCount=video.get("viewCount"),
            )
            for video in videos
        ]

    def print_search_results(
        self, search_results: Dict[str, Any], config: DisplayConfig
    ) -> str:
        output = []
        global_index = 1  # Initialize global index

        def format_item(item, fields):
            nonlocal global_index
            item_info = ", ".join(
                f"{BingSearchClient.FIELD_NAME_MAPPING.get(field, field)}: {getattr(item, field)}"
                for field in fields
            )
            formatted_item = f"{global_index}.) {item_info}"
            global_index += 1
            return formatted_item

        if config.show_entities and "entities" in search_results:
            entities_output = ["Entities:"] + [
                format_item(entity, config.entity_fields)
                for entity in search_results["entities"]
            ]
            output.append("\n".join(entities_output))

        if config.show_related_queries and "related_queries" in search_results:
            related_queries_output = ["Related Queries:"] + [
                f"{global_index}. {query}"
                for query in search_results["related_queries"]
            ]
            global_index += len(search_results["related_queries"])
            output.append("\n".join(related_queries_output))

        if config.show_web_pages and "web_pages" in search_results:
            web_pages_output = ["Web Pages:"] + [
                format_item(web_page, config.web_page_fields)
                for web_page in search_results["web_pages"]
            ]
            output.append("\n".join(web_pages_output))

        if config.show_videos and "videos" in search_results:
            videos_output = ["Videos:"] + [
                format_item(video, config.video_fields)
                for video in search_results["videos"]
            ]
            output.append("\n".join(videos_output))

        return "\n\n".join(output)

    def format_as_serp_results(self, search_results: Dict[str, Any]) -> str:
        web_pages = search_results.get("web_pages", [])

        results = []
        for web_page in web_pages:
            results.append(
                SearchResult(
                    url=getattr(web_page, "url", ""),
                    title=getattr(web_page, "name", ""),
                    dataset=f"Bing Search",
                    metadata="",
                    text=getattr(web_page, "description", "")
                    or getattr(web_page, "snippet", ""),
                )
            )
        return results
