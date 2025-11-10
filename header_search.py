"""
Header Search - Cosine similarity search on article headers
"""
import sys
from sqlalchemy import select
from app.database.connection import Database
from app.config import Config
from app.models.article_chunk import ArticleChunk
from app.models.article import Article
from app.services.embedding_service import generate_embedding
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def search_headers(query: str, top_k: int = 10):
    """
    Search headers using cosine similarity.
    
    Args:
        query: The search query text
        top_k: Number of top results to return (default: 10)
        
    Returns:
        List of tuples: (chunk_text, article_title, similarity_score, article_url)
    """
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


def display_results(results):
    """Display search results in a formatted way"""
    if not results:
        print("\nNo results found.")
        return
    
    print(f"\n{'='*100}")
    print(f"Found {len(results)} results:")
    print(f"{'='*100}\n")
    
    for idx, result in enumerate(results, 1):
        print(f"Result #{idx}")
        print(f"  Similarity Score: {result['similarity_score']:.4f}")
        print(f"  Header: {result['header_text']}")
        print(f"  Article: {result['article_title']}")
        print(f"  URL: {result['article_url']}")
        print(f"  HN ID: {result['hn_id']}")
        print(f"{'-'*100}\n")


def main():
    """Main function for standalone execution"""
    if len(sys.argv) < 2:
        print("Usage: python header_search.py <query> [top_k]")
        print("\nExample:")
        print("  python header_search.py 'machine learning' 5")
        print("  python header_search.py 'database optimization'")
        sys.exit(1)
    
    # Get query from command line arguments
    query = sys.argv[1]
    top_k = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    print(f"\nSearching for: '{query}'")
    print(f"Retrieving top {top_k} results...\n")
    
    # Perform search
    results = search_headers(query, top_k)
    
    # Display results
    display_results(results)


if __name__ == "__main__":
    main()

