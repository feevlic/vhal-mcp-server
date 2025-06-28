"""Web scraping functionality for vHAL documentation.

This module handles scraping Android vHAL documentation from various sources.
Includes caching and performance optimizations.
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Optional, Dict
from functools import lru_cache
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class VhalDocumentationScraper:
    """Optimized scraper for Android vHAL documentation with caching and parallel processing."""
    
    BASE_URL = "https://source.android.com/docs/automotive/vhal"
    CONTENT_LIMIT = 5000
    TIMEOUT = 5  # Even faster timeout for quicker failures
    MAX_WORKERS = 4  # Increased parallel workers
    
    # Cache for scraped content (expires after 1 hour) - now class-level for persistence
    _content_cache: Dict[str, tuple] = {}
    _cache_duration = 3600  # 1 hour in seconds
    _session = None  # Reuse session across all requests
    
    KNOWN_PAGES = [
        "https://source.android.com/docs/automotive/vhal",
        "https://source.android.com/docs/automotive/vhal/vhal-interface", 
        "https://source.android.com/docs/automotive/vhal/property-configuration",
        "https://source.android.com/docs/automotive/vhal/special-properties",
        "https://source.android.com/docs/automotive/vhal/seat-steering"
        "https://source.android.com/docs/automotive/vhal/adas-properties"
        "https://source.android.com/docs/automotive/vhal/reference-implementation"
        "https://source.android.com/docs/automotive/vhal/vhal_debug"
        "https://source.android.com/docs/automotive/vhal/native-client"
    ]
    
    @classmethod
    def _is_cache_valid(cls, url: str) -> bool:
        """Check if cached content is still valid."""
        if url not in cls._content_cache:
            return False
        _, timestamp = cls._content_cache[url]
        return time.time() - timestamp < cls._cache_duration
    
    @classmethod
    def _get_cached_content(cls, url: str) -> Optional[str]:
        """Get cached content if valid."""
        if cls._is_cache_valid(url):
            content, _ = cls._content_cache[url]
            return content
        return None
    
    @classmethod
    def _cache_content(cls, url: str, content: str) -> None:
        """Cache content with timestamp."""
        cls._content_cache[url] = (content, time.time())
    
    @classmethod
    def scrape_page(cls, url: str) -> Optional[str]:
        """Scrape content from a single page with caching."""
        # Check cache first
        cached_content = cls._get_cached_content(url)
        if cached_content is not None:
            return cached_content
        
        try:
            # Use persistent session for better performance
            if cls._session is None:
                cls._session = requests.Session()
                cls._session.headers.update({
                    'User-Agent': 'vHAL-MCP-Server/1.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive'
                })
                # Configure session for better performance
                from requests.adapters import HTTPAdapter
                from urllib3.util.retry import Retry
                retry_strategy = Retry(
                    total=2,
                    backoff_factor=0.1,
                    status_forcelist=[429, 500, 502, 503, 504],
                )
                adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=20)
                cls._session.mount("http://", adapter)
                cls._session.mount("https://", adapter)
            session = cls._session
            
            response = session.get(url, timeout=cls.TIMEOUT)
            response.raise_for_status()
            
            # Optimized parsing
            soup = BeautifulSoup(response.content, 'lxml')  # lxml is faster than html.parser
            
            # Remove unwanted elements more efficiently
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # More efficient text extraction with targeted content
            # Remove more noise elements
            for element in soup(['aside', 'iframe', 'noscript', 'meta', 'link']):
                element.decompose()
            
            # Focus on main content areas
            main_content = soup.find('main') or soup.find('article') or soup.find(class_='content') or soup
            text = main_content.get_text(separator=' ', strip=True)
            
            # Optimized whitespace cleanup
            import re
            clean_text = re.sub(r'\s+', ' ', text).strip()
            
            result = clean_text[:cls.CONTENT_LIMIT]
            
            # Cache the result
            cls._cache_content(url, result)
            
            return result
            
        except Exception:
            return None
    
    @classmethod
    def scrape_pages_parallel(cls, urls: List[str]) -> List[str]:
        """Scrape multiple pages in parallel for better performance."""
        results = []
        
        # Check cache first for all URLs
        cached_results = []
        urls_to_scrape = []
        
        for url in urls:
            cached_content = cls._get_cached_content(url)
            if cached_content is not None:
                cached_results.append(cached_content)
            else:
                urls_to_scrape.append(url)
        
        # Add cached results immediately
        results.extend(cached_results)
        
        # Only scrape uncached URLs
        if urls_to_scrape:
            with ThreadPoolExecutor(max_workers=cls.MAX_WORKERS) as executor:
                # Submit all tasks
                future_to_url = {executor.submit(cls.scrape_page, url): url for url in urls_to_scrape}
                
                # Collect results as they complete
                for future in as_completed(future_to_url, timeout=cls.TIMEOUT * 2):
                    try:
                        content = future.result(timeout=cls.TIMEOUT)
                        if content:
                            results.append(content)
                    except Exception:
                        continue  # Skip failed requests
        
        return results
    
    @classmethod
    @lru_cache(maxsize=1)  # Cache discovered pages for session
    def discover_pages(cls) -> List[str]:
        """Discover vHAL documentation pages with caching."""
        try:
            session = getattr(cls, '_session', None)
            if session is None:
                cls._session = requests.Session()
                session = cls._session
            
            response = session.get(cls.BASE_URL, timeout=cls.TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            discovered_links = set()  # Use set to avoid duplicates
            
            # More targeted link discovery
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and ('vhal' in href.lower() or 'vehicle' in href.lower()):
                    full_url = urljoin(cls.BASE_URL, href)
                    if full_url.startswith('https://source.android.com/docs/automotive'):
                        discovered_links.add(full_url)
            
            # Combine with known pages and limit results
            all_links = list(discovered_links.union(set(cls.KNOWN_PAGES)))
            return all_links[:8]  # Reduced to 8 for faster processing
            
        except Exception:
            return cls.KNOWN_PAGES[:6]  # Return fewer known pages on error
