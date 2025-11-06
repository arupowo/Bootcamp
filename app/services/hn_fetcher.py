import requests
from typing import List, Dict, Optional
from datetime import datetime
import json


def fetch_top_story_ids(limit: int = 10) -> List[int]:
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        story_ids = response.json()
        return story_ids[:limit]
    except requests.RequestException as e:
        print(f"Error fetching top stories: {e}")
        return []


def fetch_new_story_ids(limit: int = 10) -> List[int]:
    url = "https://hacker-news.firebaseio.com/v0/newstories.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        story_ids = response.json()
        return story_ids[:limit]
    except requests.RequestException as e:
        print(f"Error fetching new stories: {e}")
        return []


def fetch_best_story_ids(limit: int = 10) -> List[int]:
    url = "https://hacker-news.firebaseio.com/v0/beststories.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        story_ids = response.json()
        return story_ids[:limit]
    except requests.RequestException as e:
        print(f"Error fetching best stories: {e}")
        return []


def fetch_story_details(story_id: int) -> Optional[Dict]:
    url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching story {story_id}: {e}")
        return None


def extract_tags(title: str, url: str = "") -> str:
    tags = []
    
    # Common tech keywords
    keywords = [
        'python', 'javascript', 'react', 'node', 'rust', 'go', 'java',
        'ai', 'ml', 'machine learning', 'deep learning', 'api', 'web',
        'security', 'crypto', 'blockchain', 'startup', 'coding', 'programming',
        'linux', 'docker', 'kubernetes', 'cloud', 'aws', 'azure', 'gcp',
        'database', 'sql', 'nosql', 'frontend', 'backend', 'fullstack'
    ]
    
    text = (title + " " + url).lower()
    for keyword in keywords:
        if keyword.lower() in text:
            tags.append(keyword)
    
    return json.dumps(tags) if tags else None


def fetch_articles(story_ids: List[int], story_type: str = 'top') -> List[Dict]:
    articles = []
    
    for story_id in story_ids:
        story = fetch_story_details(story_id)
        if story and story.get('type') == 'story':
            url = story.get('url', '')
            title = story.get('title', 'No title')
            
            article = {
                'hn_id': story.get('id'),
                'title': title,
                'url': url,
                'hn_url': f"https://news.ycombinator.com/item?id={story_id}",
                'author': story.get('by', 'Unknown'),
                'score': story.get('score', 0),
                'comment_count': story.get('descendants', 0),
                'created_at': datetime.fromtimestamp(story.get('time', 0)) if story.get('time') else None,
                'tags': extract_tags(title, url)
            }
            articles.append(article)
    
    return articles


def fetch_top_articles(limit: int = 10) -> List[Dict]:
    story_ids = fetch_top_story_ids(limit)
    return fetch_articles(story_ids, 'top')


def fetch_trending_articles(limit: int = 10) -> List[Dict]:
    # Get top stories and new stories
    top_ids = fetch_top_story_ids(limit * 2)
    new_ids = fetch_new_story_ids(limit * 2)
    
    # Combine and deduplicate
    all_ids = list(set(top_ids + new_ids))[:limit * 2]
    
    articles = fetch_articles(all_ids, 'trending')
    
    # Sort by score and return top N
    articles.sort(key=lambda x: x['score'], reverse=True)
    return articles[:limit]


def fetch_new_articles(limit: int = 10) -> List[Dict]:
    """Fetch new articles"""
    story_ids = fetch_new_story_ids(limit)
    return fetch_articles(story_ids, 'new')


def fetch_best_articles(limit: int = 10) -> List[Dict]:
    """Fetch best articles"""
    story_ids = fetch_best_story_ids(limit)
    return fetch_articles(story_ids, 'best')

