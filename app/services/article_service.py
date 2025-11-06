"""
Article Service - Business Logic Layer
"""
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from sqlalchemy import func
from app.models.article import Article
from app.database.connection import Database
from app.services.hn_fetcher import (
    fetch_top_articles, fetch_trending_articles,
    fetch_new_articles, fetch_best_articles
)


class ArticleService:    
    def __init__(self, db: Database):
        self.db = db
    
    def save_articles_to_db(self, articles: list) -> Tuple[int, int]:
        """Save articles to database"""
        session = self.db.get_session()
        saved_count = 0
        updated_count = 0
        
        try:
            for article_data in articles:
                # Check if article already exists
                existing = session.query(Article).filter_by(hn_id=article_data['hn_id']).first()
                
                if existing:
                    # Update existing article
                    existing.title = article_data['title']
                    existing.url = article_data['url']
                    existing.score = article_data['score']
                    existing.comment_count = article_data['comment_count']
                    existing.tags = article_data.get('tags')
                    existing.fetched_at = datetime.utcnow()
                    if article_data.get('created_at'):
                        existing.created_at = article_data['created_at']
                    updated_count += 1
                else:
                    # Create new article
                    article = Article(
                        hn_id=article_data['hn_id'],
                        title=article_data['title'],
                        url=article_data['url'],
                        hn_url=article_data['hn_url'],
                        author=article_data['author'],
                        score=article_data['score'],
                        comment_count=article_data['comment_count'],
                        created_at=article_data.get('created_at'),
                        tags=article_data.get('tags')
                    )
                    session.add(article)
                    saved_count += 1
            
            session.commit()
            return saved_count, updated_count
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def fetch_and_save_top_articles(self, limit: int = 10) -> Tuple[int, int]:
        """Fetch top articles and save to database"""
        articles = fetch_top_articles(limit)
        return self.save_articles_to_db(articles)
    
    def fetch_and_save_trending_articles(self, limit: int = 10) -> Tuple[int, int]:
        """Fetch trending articles and save to database"""
        articles = fetch_trending_articles(limit)
        return self.save_articles_to_db(articles)
    
    def fetch_and_save_new_articles(self, limit: int = 10) -> Tuple[int, int]:
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

