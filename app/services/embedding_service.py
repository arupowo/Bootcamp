"""
Embedding Service - Generate vector embeddings using Google Gemini
"""
from google import genai
from google.genai import types
import os
from typing import List, Optional
import logging
from dotenv import load_dotenv
import numpy as np

load_dotenv()
logger = logging.getLogger(__name__)

# Initialize Gemini client
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key) if api_key else None
    if not client:
        logger.warning("GOOGLE_API_KEY not found in environment variables")
except Exception as e:
    client = None
    logger.warning(f"Failed to initialize Gemini client: {e}")


def generate_embeddings(texts: List[str]) -> List[Optional[List[float]]]:
    """
    Generate embeddings for multiple texts using Gemini (batch operation).
    Normalizes embeddings for accurate semantic similarity.
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        List of normalized embedding vectors (1536 dimensions each) or None for failures
    """
    if not client or not texts:
        logger.error("Gemini client not initialized or no texts provided")
        return [None] * len(texts)
    
    try:
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=texts,
            config=types.EmbedContentConfig(output_dimensionality=1536)
        )
        
        # Extract and normalize embedding vectors (1536 dimensions)
        embeddings = []
        for emb in result.embeddings:
            # Normalize the embedding for better semantic similarity
            embedding_values_np = np.array(emb.values)
            norm = np.linalg.norm(embedding_values_np)
            if norm > 0:
                normed_embedding = embedding_values_np / norm
                embeddings.append(normed_embedding.tolist())
            else:
                logger.warning("Zero vector encountered, skipping normalization")
                embeddings.append(emb.values)
        
        return embeddings
        
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        return [None] * len(texts)


def generate_embedding(text: str) -> Optional[List[float]]:
    """Generate embedding for a single text"""
    results = generate_embeddings([text])
    return results[0] if results else None

