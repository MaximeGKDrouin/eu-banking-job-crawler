import time
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger("FinanceScraper.Base")

class BaseScraper(ABC):
    def __init__(self, name: str, base_url: str, crawl_delay: float = 2.0):
        self.name = name
        self.base_url = base_url
        self.crawl_delay = crawl_delay
        self.ua = UserAgent()
        
    def _get_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive"
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(requests.RequestException),
        reraise=False
    )
    def fetch_static_page(self, url: str) -> BeautifulSoup:
        """Fetches html with exponential backoff retry logic."""
        time.sleep(self.crawl_delay)
        logger.info(f"[{self.name}] Fetching static URL: {url}")
        response = requests.get(url, headers=self._get_headers(), timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')

    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        """Must be implemented by child classes to return standardized dictionaries."""
        pass