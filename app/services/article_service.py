"""
Article Service - Business Logic Layer
"""
from typing import Dict, List, Optional, Tuple
from sqlalchemy import func
from app.models.article import Article
from app.database.connection import Database
from app.services.hn_fetcher import (
    fetch_top_articles, fetch_trending_articles,
    fetch_new_articles, fetch_best_articles
)
from app.services.scraping_service import scrape_article_content
from app.services.summary_service import generate_summary_and_tags


class ArticleService:    
    def __init__(self, db: Database):
        self.db = db
    
    def save_articles_to_db(self, articles: list) -> Tuple[int, int, List[str]]:
        """
        Save articles to database and scrape content.
        Skips saving articles if content is None.
        Optimized to batch query existing articles to avoid N+1 query problem.
        
        Returns:
            Tuple of (saved_count, updated_count, failed_urls_list)
        """
        if not articles:
            return 0, 0, []
        
        session = self.db.get_session()
        saved_count = 0
        updated_count = 0
        failed_urls = []
        
        try:
            # Batch query all existing articles to avoid N+1 problem
            hn_ids = [article_data['hn_id'] for article_data in articles]
            existing_articles = {
                article.hn_id: article 
                for article in session.query(Article).filter(Article.hn_id.in_(hn_ids)).all()
            }
            
            for article_data in articles:
                existing = existing_articles.get(article_data['hn_id'])
                
                # Scrape content if URL is available and content doesn't exist
                scraped_content = None
                generated_summary = None
                generated_tags = None
                url = article_data.get('url')
                title = article_data.get('title', '')
                
                if url and url.strip():
                    # Only scrape if content doesn't exist or is empty
                    if not existing or not existing.content:
                        scraped_content = scrape_article_content(url)
                        # Generate summary and tags ONLY for NEW articles (not existing ones)
                        # Never generate or update summary/tags for existing articles
                        if scraped_content and not existing:
                            generated_summary, generated_tags = generate_summary_and_tags(title, scraped_content)
                
                if existing:
                    # Update existing article - NEVER update summary or tags
                    existing.title = article_data['title']
                    existing.url = article_data['url']
                    existing.score = article_data['score']
                    existing.comment_count = article_data['comment_count']
                    if article_data.get('created_at'):
                        existing.created_at = article_data['created_at']
                    # Update content only if we successfully scraped it
                    if scraped_content:
                        existing.content = scraped_content
                    # DO NOT update summary or tags for existing articles
                    updated_count += 1
                else:
                    # Only create new article if content was successfully scraped
                    if scraped_content is not None:
                        article = Article(
                            hn_id=article_data['hn_id'],
                            title=article_data['title'],
                            url=article_data['url'],
                            author=article_data['author'],
                            score=article_data['score'],
                            comment_count=article_data['comment_count'],
                            created_at=article_data.get('created_at'),
                            tags=generated_tags,
                            content=scraped_content,
                            summary=generated_summary
                        )
                        session.add(article)
                        saved_count += 1
                    else:
                        # Track failed URLs for new articles that weren't saved (only if URL exists)
                        if url and url.strip():
                            failed_urls.append(url)
            
            session.commit()
            return saved_count, updated_count, failed_urls
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def fetch_and_save_top_articles(self, limit: int = 10) -> Tuple[int, int, List[str]]:
        """Fetch top articles and save to database"""
        articles = fetch_top_articles(limit)
        return self.save_articles_to_db(articles)
    
    def fetch_and_save_trending_articles(self, limit: int = 10) -> Tuple[int, int, List[str]]:
        """Fetch trending articles and save to database"""
        articles = fetch_trending_articles(limit)
        return self.save_articles_to_db(articles)
    
    def fetch_and_save_new_articles(self, limit: int = 10) -> Tuple[int, int, List[str]]:
        """Fetch new articles and save to database"""
        articles = fetch_new_articles(limit)
        return self.save_articles_to_db(articles)
    
    def get_articles(
        self,
        page: int = 1,
        per_page: int = 20,
        keyword: Optional[str] = None,
        author: Optional[str] = None,
        min_score: Optional[int] = None,
        max_score: Optional[int] = None,
        tag: Optional[str] = None,
        sort_by: str = 'score',
        order: str = 'desc'
    ) -> Dict:
        session = self.db.get_session()
        try:
            # Build query
            query = session.query(Article)
            
            # Filter by keyword (search in title)
            if keyword:
                query = query.filter(Article.title.ilike(f'%{keyword}%'))
            
            # Filter by author
            if author:
                query = query.filter(Article.author.ilike(f'%{author}%'))
            
            # Filter by score range
            if min_score is not None:
                query = query.filter(Article.score >= min_score)
            if max_score is not None:
                query = query.filter(Article.score <= max_score)
            
            # Filter by tags
            if tag:
                query = query.filter(Article.tags.ilike(f'%{tag}%'))
            
            # Sorting
            if sort_by == 'created_at':
                order_by = Article.created_at
            elif sort_by == 'comment_count':
                order_by = Article.comment_count
            else:
                order_by = Article.score
            
            if order.lower() == 'asc':
                query = query.order_by(order_by.asc())
            else:
                query = query.order_by(order_by.desc())
            
            # Pagination
            total = query.count()
            articles = query.offset((page - 1) * per_page).limit(per_page).all()
            
            return {
                'data': [article.to_dict() for article in articles],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page if total > 0 else 0
                }
            }
        finally:
            session.close()
    
    def get_article_by_id(self, article_id: int) -> Optional[Article]:
        """Get a specific article by ID"""
        session = self.db.get_session()
        
        try:
            article = session.query(Article).filter_by(id=article_id).first()
            return article
        finally:
            session.close()
    
    def get_trending_articles(self, limit: int = 10) -> List[Article]:
        """Get top trending articles from database"""
        session = self.db.get_session()
        
        try:
            articles = session.query(Article)\
                .order_by(Article.score.desc(), Article.created_at.desc())\
                .limit(limit)\
                .all()
            return articles
        finally:
            session.close()
    
    def get_stats(self) -> Dict:
        """Get statistics about articles"""
        session = self.db.get_session()
        
        try:
            total_articles = session.query(Article).count()
            avg_score = session.query(func.avg(Article.score)).scalar() or 0
            max_score = session.query(func.max(Article.score)).scalar() or 0
            total_comments = session.query(func.sum(Article.comment_count)).scalar() or 0
            
            return {
                'total_articles': total_articles,
                'average_score': round(float(avg_score), 2),
                'max_score': max_score,
                'total_comments': total_comments
            }
        finally:
            session.close()

