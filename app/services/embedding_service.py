# Embedding Service - Generate vector embeddings using Google Gemini
from google import genai
from google.genai import types
import os
from typing import List, Optional
import logging
from dotenv import load_dotenv
import numpy as np

load_dotenv()
logger = logging.getLogger(__name__)


class EmbeddingService:
    # Service class for generating vector embeddings using Google Gemini
    
    DEFAULT_MODEL = "gemini-embedding-001"
    DEFAULT_DIMENSIONS = 1536
    
    def __init__(self, api_key: Optional[str] = None, 
                 model: str = DEFAULT_MODEL,
                 dimensions: int = DEFAULT_DIMENSIONS):
        # Initialize EmbeddingService with Gemini client. Args: api_key: Google API key (defaults to GOOGLE_API_KEY env var), model: Embedding model to use, dimensions: Output dimensionality for embeddings
        self.model = model
        self.dimensions = dimensions
        self.client = None
        
        # Get API key from parameter or environment
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if api_key:
            try:
                self.client = genai.Client(api_key=api_key)
                logger.info("Gemini client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
        else:
            logger.warning("GOOGLE_API_KEY not found in environment variables")
    
    def generate_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        # Generate embeddings for multiple texts using Gemini (batch operation). Normalizes embeddings for accurate semantic similarity. Args: texts: List of text strings to embed. Returns: List of normalized embedding vectors or None for failures
        if not self.client:
            logger.error("Gemini client not initialized")
            return [None] * len(texts)
        
        if not texts:
            logger.warning("No texts provided for embedding generation")
            return []
        
        try:
            result = self.client.models.embed_content(
                model=self.model,
                contents=texts,
                config=types.EmbedContentConfig(output_dimensionality=self.dimensions)
            )
            
            # Extract and normalize embedding vectors
            embeddings = []
            for idx, emb in enumerate(result.embeddings):
                normalized_emb = self._normalize_embedding(emb.values, idx)
                embeddings.append(normalized_emb)
            
            logger.info(f"Generated {len(embeddings)} embeddings successfully")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return [None] * len(texts)
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        # Generate embedding for a single text. Args: text: Text string to embed. Returns: Normalized embedding vector or None if generation fails
        results = self.generate_embeddings([text])
        return results[0] if results else None
    
    def _normalize_embedding(self, embedding_values: List[float], index: int = 0) -> List[float]:
        # Normalize an embedding vector for better semantic similarity. Args: embedding_values: Raw embedding values, index: Index for logging purposes. Returns: Normalized embedding vector
        embedding_values_np = np.array(embedding_values)
        norm = np.linalg.norm(embedding_values_np)
        
        if norm > 0:
            normed_embedding = embedding_values_np / norm
            return normed_embedding.tolist()
        else:
            logger.warning(f"Zero vector encountered at index {index}, skipping normalization")
            return embedding_values


# Backwards compatibility: Create singleton instance
_default_service = EmbeddingService()

# Expose module-level functions for backwards compatibility
generate_embeddings = _default_service.generate_embeddings
generate_embedding = _default_service.generate_embedding

