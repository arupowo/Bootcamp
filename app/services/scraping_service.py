"""
Web Scraping Service - Extract article content from URLs using newspaper library
"""
from newspaper import Article
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def scrape_article_content(url: str, timeout: int = 10) -> Optional[str]:
    """
    Scrape article content from a given URL using the newspaper library.
    
    Args:
        url: The URL to scrape
        timeout: Request timeout in seconds (not directly used by newspaper, but kept for API consistency)
        
    Returns:
        Extracted article content as text, or None if scraping fails
    """
    if not url or url.strip() == '':
        return None
    
    try:
        # Create article object
        article = Article(url)
        
        # Download and parse the article
        article.download()
        article.parse()
        
        # Get the cleaned article text
        content = article.text
        
        # Limit content length (e.g., first 50000 characters)
        if content and len(content) > 50000:
            content = content[:50000] + '...'
        
        return content if content and len(content) > 50 else None
        
    except Exception as e:
        logger.warning(f"Error scraping content from {url}: {e}")
        return None

