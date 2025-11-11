# HackerNews Fetcher Service - Fetch articles from HackerNews API
import requests
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class HNFetcher:
    # Service class for fetching articles from HackerNews API
    
    BASE_URL = "https://hacker-news.firebaseio.com/v0"
    DEFAULT_TIMEOUT = 10
    
    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        # Initialize HNFetcher service. Args: timeout: Request timeout in seconds
        self.timeout = timeout
    
    def fetch_story_ids(self, story_type: str, limit: int = 10) -> List[int]:
        # Fetch story IDs from HackerNews API. Args: story_type: Type of stories ('top', 'new', 'best'), limit: Maximum number of story IDs to fetch. Returns: List of story IDs
        url = f"{self.BASE_URL}/{story_type}stories.json"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            story_ids = response.json()
            return story_ids[:limit]
        except requests.RequestException as e:
            logger.error(f"Error fetching {story_type} stories: {e}")
            return []
    
    def fetch_top_story_ids(self, limit: int = 10) -> List[int]:
        # Fetch top story IDs
        return self.fetch_story_ids('top', limit)
    
    def fetch_new_story_ids(self, limit: int = 10) -> List[int]:
        # Fetch new story IDs
        return self.fetch_story_ids('new', limit)
    
    def fetch_best_story_ids(self, limit: int = 10) -> List[int]:
        # Fetch best story IDs
        return self.fetch_story_ids('best', limit)
    
    def fetch_story_details(self, story_id: int) -> Optional[Dict]:
        # Fetch detailed information for a specific story. Args: story_id: HackerNews story ID. Returns: Story details dictionary or None if fetch fails
        url = f"{self.BASE_URL}/item/{story_id}.json"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching story {story_id}: {e}")
            return None
    
    def fetch_articles(self, story_ids: List[int], story_type: str = 'top') -> List[Dict]:
        # Fetch article details for multiple story IDs. Args: story_ids: List of HackerNews story IDs, story_type: Type of stories (for metadata only). Returns: List of article dictionaries with structured data
        articles = []
        
        for story_id in story_ids:
            story = self.fetch_story_details(story_id)
            if story and story.get('type') == 'story':
                url = story.get('url', '')
                title = story.get('title', 'No title')
                
                article = {
                    'hn_id': story.get('id'),
                    'title': title,
                    'url': url,
                    'author': story.get('by', 'Unknown'),
                    'score': story.get('score', 0),
                    'comment_count': story.get('descendants', 0),
                    'created_at': datetime.fromtimestamp(story.get('time', 0)) if story.get('time') else None,
                    'tags': None  # Tags will be generated later when content is scraped
                }
                articles.append(article)
        
        logger.info(f"Fetched {len(articles)} articles out of {len(story_ids)} story IDs")
        return articles
    
    def fetch_top_articles(self, limit: int = 10) -> List[Dict]:
        # Fetch top articles from HackerNews. Args: limit: Maximum number of articles to fetch. Returns: List of top articles
        story_ids = self.fetch_top_story_ids(limit)
        return self.fetch_articles(story_ids, 'top')
    
    def fetch_trending_articles(self, limit: int = 10) -> List[Dict]:
        # Fetch trending articles by combining top and new stories. Args: limit: Maximum number of articles to fetch. Returns: List of trending articles sorted by score
        # Get top stories and new stories
        top_ids = self.fetch_top_story_ids(limit * 2)
        new_ids = self.fetch_new_story_ids(limit * 2)
        
        # Combine and deduplicate
        all_ids = list(set(top_ids + new_ids))[:limit * 2]
        
        articles = self.fetch_articles(all_ids, 'trending')
        
        # Sort by score and return top N
        articles.sort(key=lambda x: x['score'], reverse=True)
        return articles[:limit]
    
    def fetch_new_articles(self, limit: int = 10) -> List[Dict]:
        # Fetch new articles from HackerNews. Args: limit: Maximum number of articles to fetch. Returns: List of new articles
        story_ids = self.fetch_new_story_ids(limit)
        return self.fetch_articles(story_ids, 'new')
    
    def fetch_best_articles(self, limit: int = 10) -> List[Dict]:
        # Fetch best articles from HackerNews. Args: limit: Maximum number of articles to fetch. Returns: List of best articles
        story_ids = self.fetch_best_story_ids(limit)
        return self.fetch_articles(story_ids, 'best')


# Backwards compatibility: Create singleton instance
_default_fetcher = HNFetcher()

# Expose module-level functions for backwards compatibility
fetch_top_story_ids = _default_fetcher.fetch_top_story_ids
fetch_new_story_ids = _default_fetcher.fetch_new_story_ids
fetch_best_story_ids = _default_fetcher.fetch_best_story_ids
fetch_story_details = _default_fetcher.fetch_story_details
fetch_articles = _default_fetcher.fetch_articles
fetch_top_articles = _default_fetcher.fetch_top_articles
fetch_trending_articles = _default_fetcher.fetch_trending_articles
fetch_new_articles = _default_fetcher.fetch_new_articles
fetch_best_articles = _default_fetcher.fetch_best_articles

