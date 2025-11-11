# UI Helper - Utility functions for the Streamlit UI
import re
from typing import List, Dict


class UIHelper:
    # Helper class for UI-related utilities
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        # Extract URLs from text. Args: text: Text to extract URLs from. Returns: List of extracted URLs
        # Pattern that catches most URLs including those with slashes
        url_pattern = r'https?://[^\s<>"\'\)\]]+(?:/[^\s<>"\'\)\]]*)?'
        urls = re.findall(url_pattern, text)
        
        # Clean up URLs - remove trailing punctuation
        cleaned_urls = []
        for url in urls:
            url = url.rstrip('.,;:!?')
            if url:
                cleaned_urls.append(url)
        
        return list(set(cleaned_urls))  # Remove duplicates
    
    @staticmethod
    def generate_suggested_questions(retrieved_headers: List[Dict]) -> List[str]:
        # Generate 3 suggested follow-up questions based on retrieved context. Args: retrieved_headers: List of retrieved header dictionaries. Returns: List of 3 suggested questions
        if not retrieved_headers or len(retrieved_headers) == 0:
            return []
        
        suggestions = []
        
        # Take up to 3 articles for suggestions
        for header in retrieved_headers[:3]:
            article_title = header['article_title']
            
            # Generate question based on article title
            if "machine learning" in article_title.lower() or "AI" in article_title.lower():
                question = f"Tell me more about {article_title[:40]}..."
            elif "python" in article_title.lower() or "programming" in article_title.lower():
                question = f"What are the key points in {article_title[:30]}?"
            else:
                question = f"Explain more about {article_title[:40]}..."
            
            suggestions.append(question)
        
        # Ensure we have exactly 3 suggestions
        while len(suggestions) < 3:
            suggestions.append("What else is trending in tech?")
        
        return suggestions[:3]
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 50) -> str:
        # Truncate text to max length and add ellipsis. Args: text: Text to truncate, max_length: Maximum length. Returns: Truncated text with ellipsis if needed
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text

