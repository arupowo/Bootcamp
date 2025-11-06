"""
LangChain Tools for HackerNews Article Operations
"""
from langchain.tools import StructuredTool, tool
from typing import Optional
from pydantic.v1 import BaseModel, Field
from app.utils.api_client import (
    fetch_top_articles,
    fetch_trending_articles,
    fetch_new_articles,
    get_articles,
    get_article_by_id,
    get_trending_articles,
    get_stats
)


class FetchTopArticlesInput(BaseModel):
    limit: int = Field(default=10, description="Number of articles to fetch")

def fetch_top_hn_articles(limit: int = 10) -> str:
    """Fetch top articles from HackerNews API and store them in the database.
    
    Args:
        limit: Number of articles to fetch (default: 10)
    
    Returns:
        A string describing how many articles were saved and updated
    """
    try:
        result = fetch_top_articles(limit)
        if result.get('success'):
            return f"Successfully fetched top articles. Saved: {result['saved']}, Updated: {result['updated']}"
        else:
            return f"Error fetching articles: {result.get('error', 'Unknown error')}"
    except Exception as e:
        return f"Error: {str(e)}"


class FetchTrendingArticlesInput(BaseModel):
    limit: int = Field(default=10, description="Number of articles to fetch")

def fetch_trending_hn_articles(limit: int = 10) -> str:
    """Fetch trending articles from HackerNews API and store them in the database.
    
    Args:
        limit: Number of articles to fetch (default: 10)
    
    Returns:
        A string describing how many articles were saved and updated
    """
    try:
        result = fetch_trending_articles(limit)
        if result.get('success'):
            return f"Successfully fetched trending articles. Saved: {result['saved']}, Updated: {result['updated']}"
        else:
            return f"Error fetching articles: {result.get('error', 'Unknown error')}"
    except Exception as e:
        return f"Error: {str(e)}"


class FetchNewArticlesInput(BaseModel):
    limit: int = Field(default=10, description="Number of articles to fetch")

def fetch_new_hn_articles(limit: int = 10) -> str:
    """Fetch new articles from HackerNews API and store them in the database.
    
    Args:
        limit: Number of articles to fetch (default: 10)
    
    Returns:
        A string describing how many articles were saved and updated
    """
    try:
        result = fetch_new_articles(limit)
        if result.get('success'):
            return f"Successfully fetched new articles. Saved: {result['saved']}, Updated: {result['updated']}"
        else:
            return f"Error fetching articles: {result.get('error', 'Unknown error')}"
    except Exception as e:
        return f"Error: {str(e)}"


class SearchArticlesInput(BaseModel):
    keyword: Optional[str] = Field(default=None, description="Search keyword to find in article titles")
    author: Optional[str] = Field(default=None, description="Filter by author name")
    min_score: Optional[int] = Field(default=None, description="Minimum score filter")
    max_score: Optional[int] = Field(default=None, description="Maximum score filter")
    tag: Optional[str] = Field(default=None, description="Filter by tag")
    sort_by: str = Field(default='score', description="Sort field: score, created_at, comment_count")
    order: str = Field(default='desc', description="Sort order: asc or desc")
    limit: int = Field(default=10, description="Maximum number of articles to return")

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
    """Search and retrieve articles from the database with various filters.
    
    Args:
        keyword: Search keyword to find in article titles
        author: Filter by author name
        min_score: Minimum score filter
        max_score: Maximum score filter
        tag: Filter by tag
        sort_by: Sort field (score, created_at, comment_count)
        order: Sort order (asc, desc)
        limit: Maximum number of articles to return (default: 10)
    
    Returns:
        A formatted string with article summaries
    """
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
                summary += f"{i}. {article.get('title', 'N/A')}\n"
                summary += f"   Author: {article.get('author', 'N/A')}\n"
                summary += f"   Score: {article.get('score', 0)}\n"
                summary += f"   Comments: {article.get('comment_count', 0)}\n"
                summary += f"   URL: {article.get('url', 'N/A')}\n"
                if article.get('tags'):
                    summary += f"   Tags: {article.get('tags')}\n"
                summary += "\n"
            return summary
        else:
            return "No articles found matching the criteria."
    except Exception as e:
        return f"Error searching articles: {str(e)}"


class GetArticleDetailsInput(BaseModel):
    article_id: int = Field(description="The database ID of the article")

def get_article_details(article_id: int) -> str:
    """Get detailed information about a specific article by its database ID.
    
    Args:
        article_id: The database ID of the article
    
    Returns:
        A formatted string with article details
    """
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
            details += f"HackerNews URL: {article.get('hn_url', 'N/A')}\n"
            if article.get('tags'):
                details += f"Tags: {article.get('tags')}\n"
            details += f"Created: {article.get('created_at', 'N/A')}\n"
            return details
        else:
            return f"Article with ID {article_id} not found."
    except Exception as e:
        return f"Error getting article details: {str(e)}"


class GetTrendingArticlesInput(BaseModel):
    limit: int = Field(default=10, description="Number of articles to return")

def get_trending_articles_from_db(limit: int = 10) -> str:
    """Get trending articles from the database, sorted by score.
    
    Args:
        limit: Number of articles to return (default: 10)
    
    Returns:
        A formatted string with trending article summaries
    """
    try:
        result = get_trending_articles(limit)
        if result.get('success') and result.get('data'):
            articles = result['data']
            summary = f"Top {len(articles)} Trending Articles:\n\n"
            for i, article in enumerate(articles, 1):
                summary += f"{i}. {article.get('title', 'N/A')}\n"
                summary += f"   Author: {article.get('author', 'N/A')}\n"
                summary += f"   Score: {article.get('score', 0)}\n"
                summary += f"   Comments: {article.get('comment_count', 0)}\n"
                summary += "\n"
            return summary
        else:
            return "No trending articles found."
    except Exception as e:
        return f"Error getting trending articles: {str(e)}"


def get_article_statistics() -> str:
    """Get statistics about articles in the database.
    
    Returns:
        A formatted string with database statistics
    """
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
    """Return all available tools"""
    return [
        StructuredTool.from_function(
            func=fetch_top_hn_articles,
            name="fetch_top_hn_articles",
            description="Fetch top articles from HackerNews API and store them in the database",
            args_schema=FetchTopArticlesInput
        ),
        StructuredTool.from_function(
            func=fetch_trending_hn_articles,
            name="fetch_trending_hn_articles",
            description="Fetch trending articles from HackerNews API and store them in the database",
            args_schema=FetchTrendingArticlesInput
        ),
        StructuredTool.from_function(
            func=fetch_new_hn_articles,
            name="fetch_new_hn_articles",
            description="Fetch new articles from HackerNews API and store them in the database",
            args_schema=FetchNewArticlesInput
        ),
        StructuredTool.from_function(
            func=search_articles,
            name="search_articles",
            description="Search and retrieve articles from the database with various filters",
            args_schema=SearchArticlesInput
        ),
        StructuredTool.from_function(
            func=get_article_details,
            name="get_article_details",
            description="Get detailed information about a specific article by its database ID",
            args_schema=GetArticleDetailsInput
        ),
        StructuredTool.from_function(
            func=get_trending_articles_from_db,
            name="get_trending_articles_from_db",
            description="Get trending articles from the database, sorted by score",
            args_schema=GetTrendingArticlesInput
        ),
        StructuredTool.from_function(
            func=get_article_statistics,
            name="get_article_statistics",
            description="Get statistics about articles in the database"
        )
    ]

