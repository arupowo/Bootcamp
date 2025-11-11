# Chunking Service - Split articles into searchable chunks
import tiktoken
from typing import List, Dict, Optional
import logging
import json

logger = logging.getLogger(__name__)


class ChunkingService:
    # Service class for chunking articles into searchable segments
    
    DEFAULT_MODEL = "gpt-3.5-turbo"
    DEFAULT_MAX_TOKENS = 512
    CHARS_PER_TOKEN = 4  # Fallback approximation
    
    def __init__(self, model: str = DEFAULT_MODEL, max_tokens: int = DEFAULT_MAX_TOKENS):
        # Initialize ChunkingService. Args: model: Model name for token counting, max_tokens: Maximum tokens per chunk
        self.model = model
        self.max_tokens = max_tokens
        self._encoding = None
        
        # Try to initialize tiktoken encoding
        try:
            self._encoding = tiktoken.encoding_for_model(model)
        except Exception as e:
            logger.warning(f"Failed to initialize tiktoken encoding: {e}. Using fallback.")
    
    def count_tokens(self, text: str) -> int:
        # Count tokens in text using tiktoken. Args: text: Text to count tokens for. Returns: Token count
        if self._encoding:
            try:
                return len(self._encoding.encode(text))
            except Exception as e:
                logger.warning(f"Error counting tokens: {e}. Using fallback.")
        
        # Fallback: approximate 1 token = 4 characters
        return len(text) // self.CHARS_PER_TOKEN
    
    def chunk_article(
        self,
        title: str, 
        summary: str, 
        content: str, 
        author: Optional[str] = None,
        score: Optional[int] = None,
        comment_count: Optional[int] = None,
        tags: Optional[str] = None,
        created_at: Optional[str] = None,
        url: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> List[Dict]:
        # Split article into chunks for embedding with rich metadata. Args: title, summary, content, author, score, comment_count, tags, created_at, url, max_tokens. Returns: List of dicts with: chunk_text, chunk_type, chunk_index, token_count
        max_tokens = max_tokens or self.max_tokens
        chunks = []
        
        # CHUNK 1: Header (rich metadata for Stage 1 search)
        header_text = self._create_header_chunk(
            title, summary, author, score, comment_count, tags, created_at, url
        )
        
        chunks.append({
            'chunk_text': header_text,
            'chunk_type': 'header',
            'chunk_index': 0,
            'token_count': self.count_tokens(header_text)
        })
        
        # CHUNK 2+: Content chunks (for Stage 2 detailed search)
        if content and len(content.strip()) > 100:
            content_chunks = self._create_content_chunks(content, max_tokens)
            chunks.extend(content_chunks)
        
        logger.info(f"Created {len(chunks)} chunks for article: {title[:50]}")
        return chunks
    
    def _create_header_chunk(
        self,
        title: str,
        summary: str,
        author: Optional[str],
        score: Optional[int],
        comment_count: Optional[int],
        tags: Optional[str],
        created_at: Optional[str],
        url: Optional[str]
    ) -> str:
        # Create the header chunk with rich metadata
        header_parts = [f"Title: {title}"]
        
        if author:
            header_parts.append(f"Author: {author}")
        
        if score is not None:
            header_parts.append(f"Score: {score} points")
        
        if comment_count is not None:
            header_parts.append(f"Comments: {comment_count}")
        
        if created_at:
            header_parts.append(f"Published: {created_at}")
        
        if tags:
            try:
                tags_list = json.loads(tags) if isinstance(tags, str) else tags
                if tags_list:
                    tags_str = ", ".join(tags_list)
                    header_parts.append(f"Tags: {tags_str}")
            except Exception:
                header_parts.append(f"Tags: {tags}")
        
        if url:
            header_parts.append(f"URL: {url}")
        
        if summary:
            header_parts.append(f"\nSummary:\n{summary}")
        
        return "\n".join(header_parts)
    
    def _create_content_chunks(self, content: str, max_tokens: int) -> List[Dict]:
        # Split content into token-limited chunks
        chunks = []
        paragraphs = content.split('\n\n')
        current_chunk = ""
        chunk_index = 1
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            test_chunk = current_chunk + "\n\n" + para if current_chunk else para
            token_count = self.count_tokens(test_chunk)
            
            if token_count <= max_tokens:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append({
                        'chunk_text': current_chunk,
                        'chunk_type': 'content',
                        'chunk_index': chunk_index,
                        'token_count': self.count_tokens(current_chunk)
                    })
                    chunk_index += 1
                current_chunk = para
        
        # Add the last chunk
        if current_chunk:
            chunks.append({
                'chunk_text': current_chunk,
                'chunk_type': 'content',
                'chunk_index': chunk_index,
                'token_count': self.count_tokens(current_chunk)
            })
        
        return chunks


# Backwards compatibility: Create singleton instance
_default_chunker = ChunkingService()

# Expose module-level functions for backwards compatibility
count_tokens = _default_chunker.count_tokens
chunk_article = _default_chunker.chunk_article
