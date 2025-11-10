"""
Chunking Service - Split articles into searchable chunks
"""
import tiktoken
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Count tokens in text using tiktoken"""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # Fallback: approximate 1 token = 4 characters
        return len(text) // 4


def chunk_article(
    title: str, 
    summary: str, 
    content: str, 
    author: str = None,
    score: int = None,
    comment_count: int = None,
    tags: str = None,
    created_at: str = None,
    url: str = None,
    max_tokens: int = 512
) -> List[Dict]:
    """
    Split article into chunks for embedding with rich metadata.
    
    Returns list of dicts with: chunk_text, chunk_type, chunk_index, token_count
    """
    chunks = []
    
    # CHUNK 1: Header (rich metadata for Stage 1 search)
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
        # Parse tags if it's a JSON string
        import json
        try:
            tags_list = json.loads(tags) if isinstance(tags, str) else tags
            if tags_list:
                tags_str = ", ".join(tags_list)
                header_parts.append(f"Tags: {tags_str}")
        except:
            header_parts.append(f"Tags: {tags}")
    
    if url:
        header_parts.append(f"URL: {url}")
    
    if summary:
        header_parts.append(f"\nSummary:\n{summary}")
    
    header_text = "\n".join(header_parts)
    
    chunks.append({
        'chunk_text': header_text,
        'chunk_type': 'header',
        'chunk_index': 0,
        'token_count': count_tokens(header_text)
    })
    
    # CHUNK 2+: Content chunks (for Stage 2 detailed search)
    if content and len(content.strip()) > 100:
        paragraphs = content.split('\n\n')
        current_chunk = ""
        chunk_index = 1
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            test_chunk = current_chunk + "\n\n" + para if current_chunk else para
            token_count = count_tokens(test_chunk)
            
            if token_count <= max_tokens:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append({
                        'chunk_text': current_chunk,
                        'chunk_type': 'content',
                        'chunk_index': chunk_index,
                        'token_count': count_tokens(current_chunk)
                    })
                    chunk_index += 1
                current_chunk = para
        
        # Add the last chunk
        if current_chunk:
            chunks.append({
                'chunk_text': current_chunk,
                'chunk_type': 'content',
                'chunk_index': chunk_index,
                'token_count': count_tokens(current_chunk)
            })
    
    return chunks
