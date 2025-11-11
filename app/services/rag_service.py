# RAG Service - Handles Retrieval-Augmented Generation operations
import os
from typing import List, Dict, Optional, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from sqlalchemy import select
from app.database.connection import Database
from app.config import Config
from app.models.article_chunk import ArticleChunk
from app.models.article import Article
from app.services.embedding_service import generate_embedding
import logging

logger = logging.getLogger(__name__)


def search_headers(query: str, top_k: int = 10):
    # Search headers using cosine similarity. Args: query: The search query text, top_k: Number of top results to return (default: 10). Returns: List of tuples: (chunk_text, article_title, similarity_score, article_url)
    # Initialize database
    db = Database(Config.DATABASE_URL)
    session = db.get_session()
    
    try:
        # Generate embedding for the query (automatically normalized for accurate similarity)
        logger.info(f"Generating embedding for query: '{query}'")
        query_embedding = generate_embedding(query)
        
        if query_embedding is None:
            logger.error("Failed to generate embedding for query")
            return []
        
        # Perform cosine similarity search on headers
        # Using pgvector's cosine distance operator <=>
        # Lower distance = higher similarity
        logger.info("Performing cosine similarity search on headers...")
        
        query_stmt = select(
            ArticleChunk.chunk_text,
            Article.title,
            Article.url,
            Article.hn_id,
            ArticleChunk.article_id,
            ArticleChunk.embedding.cosine_distance(query_embedding).label('distance')
        ).join(
            Article,
            Article.hn_id == ArticleChunk.article_id
        ).where(
            ArticleChunk.chunk_type == 'header'
        ).where(
            ArticleChunk.embedding.isnot(None)
        ).order_by(
            'distance'
        ).limit(top_k)
        
        results = session.execute(query_stmt).all()
        
        # Convert distance to similarity score (1 - distance)
        formatted_results = [
            {
                'header_text': row[0],
                'article_title': row[1],
                'article_url': row[2],
                'hn_id': row[3],
                'article_id': row[4],
                'similarity_score': 1 - row[5]  # Convert distance to similarity
            }
            for row in results
        ]
        
        return formatted_results
        
    except Exception as e:
        logger.error(f"Error during search: {e}")
        return []
    finally:
        session.close()


class RAGService:
    # Service class for RAG operations
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash", temperature: float = 0.7):
        # Initialize RAG Service. Args: api_key: Google API key for Gemini, model: Model name to use, temperature: Temperature for generation
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        # Initialize the LLM model
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=self.model,
                google_api_key=self.api_key,
                temperature=self.temperature,
                convert_system_message_to_human=True
            )
            logger.info(f"LLM initialized successfully with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise
    
    def retrieve_context(self, query: str, top_k: int = 4) -> List[Dict]:
        # Retrieve relevant context from knowledge base. Args: query: User query, top_k: Number of results to retrieve. Returns: List of retrieved headers with metadata
        try:
            retrieved_headers = search_headers(query, top_k=top_k)
            logger.info(f"Retrieved {len(retrieved_headers)} headers for query: {query[:50]}...")
            return retrieved_headers
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    def build_context_string(self, retrieved_headers: List[Dict]) -> str:
        # Build context string from retrieved headers. Args: retrieved_headers: List of retrieved header results. Returns: Formatted context string
        if not retrieved_headers:
            return ""
        
        context = "\n\n**CONTEXT FROM KNOWLEDGE BASE:**\n\n"
        for idx, result in enumerate(retrieved_headers, 1):
            context += f"Article {idx}: {result['article_title']}\n"
            context += f"Header: {result['header_text']}\n"
            context += f"URL: {result['article_url']}\n"
            context += f"Relevance Score: {result['similarity_score']:.3f}\n\n"
        
        return context
    
    def generate_response(
        self,
        user_prompt: str,
        conversation_history: List[Dict],
        retrieved_headers: List[Dict]
    ) -> str:
        # Generate response using LLM with RAG. Args: user_prompt: Current user prompt, conversation_history: Previous conversation messages, retrieved_headers: Retrieved context. Returns: Generated response text
        # Build context
        context = self.build_context_string(retrieved_headers)
        
        # System prompt
        system_prompt = """You are a helpful AI assistant with access to a knowledge base of HackerNews articles. 
        
When provided with context from the knowledge base, use it to answer questions accurately and cite the sources.
If the context is relevant, reference the article titles and provide the URLs.
If the context is not relevant to the question, you can answer based on your general knowledge."""
        
        # Build messages
        messages = [SystemMessage(content=system_prompt)]
        
        # Add conversation history
        for msg in conversation_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        # Add current user message with context
        user_message_with_context = user_prompt
        if context:
            user_message_with_context = f"{context}\n\n**USER QUESTION:**\n{user_prompt}"
        
        messages.append(HumanMessage(content=user_message_with_context))
        
        # Get response from LLM
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def process_query(
        self,
        user_prompt: str,
        conversation_history: List[Dict]
    ) -> Tuple[str, List[Dict]]:
        # Complete RAG pipeline: retrieve + generate. Args: user_prompt: User query, conversation_history: Previous messages. Returns: Tuple of (response_text, retrieved_headers)
        # Step 1: Retrieve
        retrieved_headers = self.retrieve_context(user_prompt)
        
        # Step 2: Generate
        response_text = self.generate_response(
            user_prompt,
            conversation_history,
            retrieved_headers
        )
        
        return response_text, retrieved_headers

