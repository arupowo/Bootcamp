from sqlalchemy import Column, Integer, BigInteger, Text, DateTime, CheckConstraint, Index
from pgvector.sqlalchemy import Vector
from datetime import datetime
from app.database.connection import Base


class ArticleChunk(Base):
    __tablename__ = 'article_chunks'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    article_id = Column(BigInteger, nullable=False)  # References articles.hn_id
    chunk_text = Column(Text, nullable=False)
    chunk_type = Column(Text, nullable=False)  # 'header' or 'content'
    chunk_index = Column(Integer, nullable=False)
    embedding = Column(Vector(1536), nullable=True)  # 1536 dimensions - OpenAI compatible
    token_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint("chunk_type IN ('header', 'content')", name='check_chunk_type'),
        Index('idx_chunks_article_id', 'article_id'),
        Index('idx_chunks_type', 'chunk_type'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'article_id': self.article_id,
            'chunk_text': self.chunk_text,
            'chunk_type': self.chunk_type,
            'chunk_index': self.chunk_index,
            'token_count': self.token_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

