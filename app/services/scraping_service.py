from newspaper import Article
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def scrape_article_content(url: str, timeout: int = 10) -> Optional[str]:
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

