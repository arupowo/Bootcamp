from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from app.database.connection import Base


class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    hn_id = Column(Integer, unique=True, nullable=False, index=True)  # HackerNews ID
    title = Column(String(500), nullable=False, index=True)
    url = Column(Text, nullable=True)
    hn_url = Column(Text, nullable=False)  # HackerNews discussion URL
    author = Column(String(100), nullable=False, index=True)
    score = Column(Integer, default=0, index=True)
    comment_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=None, index=True)
    fetched_at = Column(DateTime, default=None)
    tags = Column(Text, nullable=True)  # JSON string of tags/keywords
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_score_created', 'score', 'created_at'),
        Index('idx_title_search', 'title'),
    )
    
    def to_dict(self):
        """Convert article to dictionary"""
        return {
            'id': self.id,
            'hn_id': self.hn_id,
            'title': self.title,
            'url': self.url,
            'hn_url': self.hn_url,
            'author': self.author,
            'score': self.score,
            'comment_count': self.comment_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'fetched_at': self.fetched_at.isoformat() if self.fetched_at else None,
            'tags': self.tags
        }

