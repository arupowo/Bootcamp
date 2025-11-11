# LangChain Tools for HackerNews Article Operations
from langchain.tools import tool
from typing import Optional
from app.utils.api_client import (
    fetch_top_articles,
    fetch_trending_articles,
    fetch_new_articles,
    get_articles,
    get_article_by_id,
    get_trending_articles,
    get_stats
)


@tool
def fetch_top_hn_articles(limit: int = 10) -> str:
    # Fetch top articles from HackerNews API and store them in the database. Args: limit: Number of articles to fetch (default: 10). Returns: A string describing how many articles were saved and updated
    try:
        result = fetch_top_articles(limit)
        if result.get('success'):
            return f"Successfully fetched top articles. Saved: {result['saved']}, Updated: {result['updated']}"
        else:
            return f"Error fetching articles: {result.get('error', 'Unknown error')}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def fetch_trending_hn_articles(limit: int = 10) -> str:
    # Fetch trending articles from HackerNews API and store them in the database. Args: limit: Number of articles to fetch (default: 10). Returns: A string describing how many articles were saved and updated
    try:
        result = fetch_trending_articles(limit)
        if result.get('success'):
            return f"Successfully fetched trending articles. Saved: {result['saved']}, Updated: {result['updated']}"
        else:
            return f"Error fetching articles: {result.get('error', 'Unknown error')}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def fetch_new_hn_articles(limit: int = 10) -> str:
    # Fetch new articles from HackerNews API and store them in the database. Args: limit: Number of articles to fetch (default: 10). Returns: A string describing how many articles were saved and updated
    try:
        result = fetch_new_articles(limit)
        if result.get('success'):
            return f"Successfully fetched new articles. Saved: {result['saved']}, Updated: {result['updated']}"
        else:
            return f"Error fetching articles: {result.get('error', 'Unknown error')}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def search_articles(
    keyword: Optional[str] = None,
    author: Optional[str] = None,
    min_score: Optional[int] = None,
    max_score: Optional[int] = None,
    tag: Optional[str] = None,
    sort_by: str = 'score',
    order: str = 'desc',
    limit: int = 10
) -> str:
    # Search and retrieve articles from the database with various filters. Args: keyword, author, min_score, max_score, tag, sort_by, order, limit. Returns: A formatted string with article summaries
    try:
        result = get_articles(
            page=1,
            per_page=limit,
            keyword=keyword,
            author=author,
            min_score=min_score,
            max_score=max_score,
            tag=tag,
            sort_by=sort_by,
            order=order
        )
        
        if result.get('success') and result.get('data'):
            articles = result['data']
            summary = f"Found {len(articles)} articles:\n\n"
            for i, article in enumerate(articles, 1):
                article_id = article.get('id', 'N/A')
                summary += f"{i}. {article.get('title', 'N/A')}\n"
                summary += f"   ID: {article_id}\n"
                summary += f"   Author: {article.get('author', 'N/A')}\n"
                summary += f"   Score: {article.get('score', 0)}\n"
                summary += f"   Comments: {article.get('comment_count', 0)}\n"
                url = article.get('url', 'N/A')
                if url and url != 'N/A':
                    summary += f"   Article URL: {url}\n"
                if article.get('tags'):
                    summary += f"   Tags: {article.get('tags')}\n"
                summary += "\n"
            return summary
        else:
            return "No articles found matching the criteria."
    except Exception as e:
        return f"Error searching articles: {str(e)}"


@tool
def get_article_details(article_id: int) -> str:
    # Get detailed information about a specific article by its database ID. Args: article_id: The database ID of the article. Returns: A formatted string with article details
    try:
        result = get_article_by_id(article_id)
        if result.get('success') and result.get('data'):
            article = result['data']
            details = f"Article Details:\n\n"
            details += f"Title: {article.get('title', 'N/A')}\n"
            details += f"Author: {article.get('author', 'N/A')}\n"
            details += f"Score: {article.get('score', 0)}\n"
            details += f"Comments: {article.get('comment_count', 0)}\n"
            details += f"URL: {article.get('url', 'N/A')}\n"
            if article.get('tags'):
                details += f"Tags: {article.get('tags')}\n"
            details += f"Created: {article.get('created_at', 'N/A')}\n"
            return details
        else:
            return f"Article with ID {article_id} not found."
    except Exception as e:
        return f"Error getting article details: {str(e)}"


@tool
def get_trending_articles_from_db(limit: int = 10) -> str:
    # Get trending articles from the database, sorted by score. Args: limit: Number of articles to return (default: 10). Returns: A formatted string with trending article summaries
    try:
        result = get_trending_articles(limit)
        if result.get('success') and result.get('data'):
            articles = result['data']
            summary = f"Top {len(articles)} Trending Articles:\n\n"
            for i, article in enumerate(articles, 1):
                article_id = article.get('id', 'N/A')
                summary += f"{i}. {article.get('title', 'N/A')}\n"
                summary += f"   ID: {article_id}\n"
                summary += f"   Author: {article.get('author', 'N/A')}\n"
                summary += f"   Score: {article.get('score', 0)}\n"
                summary += f"   Comments: {article.get('comment_count', 0)}\n"
                url = article.get('url', 'N/A')
                if url and url != 'N/A':
                    summary += f"   Article URL: {url}\n"
                summary += "\n"
            return summary
        else:
            return "No trending articles found."
    except Exception as e:
        return f"Error getting trending articles: {str(e)}"


@tool
def get_article_statistics() -> str:
    # Get statistics about articles in the database. Returns: A formatted string with database statistics
    try:
        result = get_stats()
        if result.get('success') and result.get('stats'):
            stats = result['stats']
            summary = "Article Statistics:\n\n"
            summary += f"Total Articles: {stats.get('total_articles', 0)}\n"
            summary += f"Average Score: {stats.get('average_score', 0):.2f}\n"
            summary += f"Max Score: {stats.get('max_score', 0)}\n"
            summary += f"Total Comments: {stats.get('total_comments', 0)}\n"
            return summary
        else:
            return "Unable to retrieve statistics."
    except Exception as e:
        return f"Error getting statistics: {str(e)}"


def get_all_tools():
    # Return all available tools
    return [
        fetch_top_hn_articles,
        fetch_trending_hn_articles,
        fetch_new_hn_articles,
        search_articles,
        get_article_details,
        get_trending_articles_from_db,
        get_article_statistics
    ]

