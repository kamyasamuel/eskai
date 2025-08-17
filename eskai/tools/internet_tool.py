import requests
from typing import Optional


class InternetTool:
    """
    Tool for web access and scraping.
    """
    def __init__(self, name: str, headers: Optional[dict] = None):
        self.name = name
        self.headers = headers or {"User-Agent": "ESKAI-Agent/1.0"}

    def fetch(self, url: str) -> str:
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.text
