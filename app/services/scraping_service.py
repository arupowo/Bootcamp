# Scraping Service - Extract article content from URLs
from newspaper import Article
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ScrapingService:
    # Service class for scraping article content from web URLs
    
    DEFAULT_TIMEOUT = 10
    MAX_CONTENT_LENGTH = 50000
    MIN_CONTENT_LENGTH = 50
    
    def __init__(self, timeout: int = DEFAULT_TIMEOUT, 
                 max_length: int = MAX_CONTENT_LENGTH,
                 min_length: int = MIN_CONTENT_LENGTH):
        # Initialize ScrapingService. Args: timeout: Request timeout in seconds, max_length: Maximum content length to extract, min_length: Minimum content length to consider valid
        self.timeout = timeout
        self.max_length = max_length
        self.min_length = min_length
    
    def scrape_article_content(self, url: str) -> Optional[str]:
        # Scrape and extract article content from a URL. Args: url: The URL to scrape. Returns: Extracted article text or None if scraping fails
        if not url or url.strip() == '':
            logger.warning("Empty URL provided for scraping")
            return None
        
        try:
            # Create article object
            article = Article(url)
            
            # Download and parse the article
            article.download()
            article.parse()
            
            # Get the cleaned article text
            content = article.text
            
            # Validate content
            if not content or len(content) < self.min_length:
                logger.warning(f"Content too short from {url}: {len(content) if content else 0} chars")
                return None
            
            # Limit content length
            if len(content) > self.max_length:
                logger.info(f"Truncating content from {url}: {len(content)} -> {self.max_length} chars")
                content = content[:self.max_length] + '...'
            
            return content
            
        except Exception as e:
            logger.warning(f"Error scraping content from {url}: {e}")
            return None
    
    def scrape_multiple(self, urls: list[str]) -> dict[str, Optional[str]]:
        # Scrape content from multiple URLs. Args: urls: List of URLs to scrape. Returns: Dictionary mapping URLs to scraped content (or None for failures)
        results = {}
        for url in urls:
            results[url] = self.scrape_article_content(url)
        return results


# Backwards compatibility: Create singleton instance
_default_scraper = ScrapingService()

# Expose module-level function for backwards compatibility
scrape_article_content = _default_scraper.scrape_article_content

