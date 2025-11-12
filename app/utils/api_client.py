# API Client - Functions to call the Flask API endpoints
import requests
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()


def get_api_base_url() -> str:
    # Get API base URL from environment or default
    return os.getenv('API_BASE_URL', 'http://localhost:5000/api')


def fetch_top_articles(limit: int = 10) -> Dict:
    # Fetch top articles from HackerNews and store in database
    response = requests.post(
        f"{get_api_base_url()}/articles/fetch/top",
        json={"limit": limit},
        headers={"Content-Type": "application/json"}
    )
    return response.json()


def fetch_trending_articles(limit: int = 10) -> Dict:
    # Fetch trending articles from HackerNews and store in database
    response = requests.post(
        f"{get_api_base_url()}/articles/fetch/trending",
        json={"limit": limit},
        headers={"Content-Type": "application/json"}
    )
    return response.json()


def fetch_new_articles(limit: int = 10) -> Dict:
    # Fetch new articles from HackerNews and store in database
    response = requests.post(
        f"{get_api_base_url()}/articles/fetch/new",
        json={"limit": limit},
        headers={"Content-Type": "application/json"}
    )
    return response.json()


def get_articles(
    page: int = 1,
    per_page: int = 20,
    keyword: Optional[str] = None,
    author: Optional[str] = None,
    min_score: Optional[int] = None,
    max_score: Optional[int] = None,
    tag: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: str = 'score',
    order: str = 'desc'
) -> Dict:
    # Get articles from database with filters
    params = {
        'page': page,
        'per_page': per_page,
        'sort_by': sort_by,
        'order': order
    }
    
    if keyword:
        params['keyword'] = keyword
    if author:
        params['author'] = author
    if min_score is not None:
        params['min_score'] = min_score
    if max_score is not None:
        params['max_score'] = max_score
    if tag:
        params['tag'] = tag
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date
    
    response = requests.get(f"{get_api_base_url()}/articles", params=params)
    return response.json()


def get_article_by_id(article_id: int) -> Dict:
    # Get a specific article by database ID
    response = requests.get(f"{get_api_base_url()}/articles/{article_id}")
    return response.json()


def get_trending_articles(limit: int = 10) -> Dict:
    # Get trending articles from database
    response = requests.get(
        f"{get_api_base_url()}/articles/trending",
        params={'limit': limit}
    )
    return response.json()


def get_stats() -> Dict:
    # Get statistics about articles
    response = requests.get(f"{get_api_base_url()}/articles/stats")
    return response.json()

