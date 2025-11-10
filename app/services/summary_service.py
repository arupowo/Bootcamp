from groq import Groq
from typing import Optional
import logging
import os
import json
import re

logger = logging.getLogger(__name__)

# Initialize Groq client
try:
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        client = Groq(api_key=api_key)
    else:
        client = None
        logger.warning("GROQ_API_KEY not found in environment variables")
except Exception as e:
    client = None
    logger.warning(f"Failed to initialize Groq client: {e}")


def generate_summary_and_tags(title: str, content: str) -> tuple[Optional[str], Optional[str]]:
    """
    Generate both summary and tags in a single LLM call for efficiency.
    
    Args:
        title: Article title
        content: Article content (will be truncated if too long)
        
    Returns:
        Tuple of (summary, tags_json_string) or (None, None) if generation fails
    """
    if not client:
        logger.warning("Groq client not initialized. Cannot generate summary and tags.")
        return None, None
    
    if not content or len(content.strip()) < 100:
        logger.warning("Content too short to generate summary and tags")
        return None, None
    
    try:
        # Truncate content if too long (Groq has token limits)
        # Keep first 8000 characters for context
        content_preview = content[:8000] if len(content) > 8000 else content
        
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
        
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
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
                if len(summary) > 500:
                    summary = summary[:497] + "..."
            else:
                summary = None
            
            # Validate and format tags
            if isinstance(tags, list) and len(tags) > 0:
                tags = tags[:10]  # Limit to 10 tags max
                tags_json = json.dumps(tags)
            else:
                tags_json = None
            
            return summary, tags_json
            
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract from text
            logger.warning(f"Failed to parse combined response as JSON, attempting extraction: {response}")
            # Try to find summary and tags in the response
            summary = None
            tags_json = None
            
            # Try to extract summary (look for "summary" field)
            summary_match = re.search(r'"summary"\s*:\s*"([^"]+)"', response, re.IGNORECASE)
            if summary_match:
                summary = summary_match.group(1).strip()
                if len(summary) > 500:
                    summary = summary[:497] + "..."
            
            # Try to extract tags array
            tags_match = re.search(r'"tags"\s*:\s*\[([^\]]+)\]', response, re.IGNORECASE)
            if tags_match:
                tags_str = tags_match.group(1)
                tag_matches = re.findall(r'["\']([^"\']+)["\']', tags_str)
                if tag_matches:
                    tags = tag_matches[:10]
                    tags_json = json.dumps(tags)
            
            return summary, tags_json
        
    except Exception as e:
        logger.warning(f"Error generating summary and tags: {e}")
        return None, None

