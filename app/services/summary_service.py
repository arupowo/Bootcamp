# Summary Service - Generate article summaries and tags using Groq LLM
from groq import Groq
from typing import Optional, Tuple
import logging
import os
import json
import re

logger = logging.getLogger(__name__)


class SummaryService:
    # Service class for generating article summaries and tags using Groq LLM
    
    DEFAULT_MODEL = "openai/gpt-oss-120b"
    MAX_CONTENT_LENGTH = 8000
    MAX_SUMMARY_LENGTH = 500
    MAX_TAGS = 10
    MIN_CONTENT_LENGTH = 100
    
    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL):
        # Initialize SummaryService with Groq client. Args: api_key: Groq API key (defaults to GROQ_API_KEY env var), model: Model to use for generation
        self.model = model
        self.client = None
        
        # Get API key from parameter or environment
        api_key = api_key or os.getenv('GROQ_API_KEY')
        
        if api_key:
            try:
                self.client = Groq(api_key=api_key)
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
        else:
            logger.warning("GROQ_API_KEY not found in environment variables")
    
    def generate_summary_and_tags(self, title: str, content: str) -> Tuple[Optional[str], Optional[str]]:
        # Generate both summary and tags in a single LLM call for efficiency. Args: title: Article title, content: Article content (will be truncated if too long). Returns: Tuple of (summary, tags_json_string) or (None, None) if generation fails
        if not self.client:
            logger.warning("Groq client not initialized. Cannot generate summary and tags.")
            return None, None
        
        if not content or len(content.strip()) < self.MIN_CONTENT_LENGTH:
            logger.warning("Content too short to generate summary and tags")
            return None, None
        
        try:
            # Truncate content if too long (Groq has token limits)
            content_preview = content[:self.MAX_CONTENT_LENGTH] if len(content) > self.MAX_CONTENT_LENGTH else content
            
            prompt = f"""Analyze the following article and provide:
1. A concise summary (2-3 sentences, maximum 200 words) for RAG metadata search. Focus on key topics, technologies, and main points.
2. 5-10 relevant tags/keywords as a JSON array. Focus on:
   - Programming languages, frameworks, and technologies mentioned
   - Main topics and subject areas
   - Tools, platforms, or services discussed
   - Industry or domain (e.g., AI, security, web development, etc.)

Title: {title}

Content:
{content_preview}

Return your response in this exact JSON format (no markdown, no code blocks, just pure JSON):
{{
  "summary": "your summary here",
  "tags": ["tag1", "tag2", "tag3"]
}}"""
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.6,
                max_completion_tokens=500,
                top_p=1,
                reasoning_effort="medium",
                stream=False,
                stop=None
            )
            
            response = completion.choices[0].message.content.strip()
            
            # Parse JSON response
            return self._parse_llm_response(response)
            
        except Exception as e:
            logger.warning(f"Error generating summary and tags: {e}")
            return None, None
    
    def _parse_llm_response(self, response: str) -> Tuple[Optional[str], Optional[str]]:
        # Parse LLM response to extract summary and tags. Args: response: Raw LLM response string. Returns: Tuple of (summary, tags_json_string)
        try:
            # Remove markdown code blocks if present
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()
            
            data = json.loads(response)
            summary = data.get('summary', '').strip()
            tags = data.get('tags', [])
            
            # Validate and format summary
            if summary:
                if len(summary) > self.MAX_SUMMARY_LENGTH:
                    summary = summary[:self.MAX_SUMMARY_LENGTH-3] + "..."
            else:
                summary = None
            
            # Validate and format tags
            if isinstance(tags, list) and len(tags) > 0:
                tags = tags[:self.MAX_TAGS]
                tags_json = json.dumps(tags)
            else:
                tags_json = None
            
            return summary, tags_json
            
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract from text
            logger.warning(f"Failed to parse combined response as JSON, attempting extraction")
            return self._extract_from_text(response)
    
    def _extract_from_text(self, response: str) -> Tuple[Optional[str], Optional[str]]:
        # Extract summary and tags from plain text when JSON parsing fails. Args: response: Raw text response. Returns: Tuple of (summary, tags_json_string)
        summary = None
        tags_json = None
        
        # Try to extract summary (look for "summary" field)
        summary_match = re.search(r'"summary"\s*:\s*"([^"]+)"', response, re.IGNORECASE)
        if summary_match:
            summary = summary_match.group(1).strip()
            if len(summary) > self.MAX_SUMMARY_LENGTH:
                summary = summary[:self.MAX_SUMMARY_LENGTH-3] + "..."
        
        # Try to extract tags array
        tags_match = re.search(r'"tags"\s*:\s*\[([^\]]+)\]', response, re.IGNORECASE)
        if tags_match:
            tags_str = tags_match.group(1)
            tag_matches = re.findall(r'["\']([^"\']+)["\']', tags_str)
            if tag_matches:
                tags = tag_matches[:self.MAX_TAGS]
                tags_json = json.dumps(tags)
        
        return summary, tags_json


# Backwards compatibility: Create singleton instance
_default_service = SummaryService()

# Expose module-level function for backwards compatibility
generate_summary_and_tags = _default_service.generate_summary_and_tags

