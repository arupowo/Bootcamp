# API Routes - REST Endpoints
from flask import Blueprint, jsonify, request
from app.database.connection import Database
from app.services.article_service import ArticleService

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Global variables for database and service (will be initialized)
article_service_instance = None


def init_routes(db: Database):
    # Initialize routes with database instance
    global article_service_instance
    article_service_instance = ArticleService(db)


@api_bp.route('/health', methods=['GET'])
def health_check():
    # Health check endpoint
    return jsonify({'status': 'healthy', 'message': 'HackerNews API is running'})


@api_bp.route('/articles/fetch/top', methods=['POST'])
def fetch_top():
    # Fetch and store top articles
    limit = request.json.get('limit', 10) if request.json else 10
    
    try:
        saved_count, updated_count, failed_urls = article_service_instance.fetch_and_save_top_articles(limit)
        return jsonify({
            'success': True,
            'saved': saved_count,
            'updated': updated_count,
            'failed_urls': failed_urls,
            'failed_count': len(failed_urls),
            'message': f'Successfully fetched articles (saved: {saved_count}, updated: {updated_count}, failed: {len(failed_urls)})'
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/articles/fetch/trending', methods=['POST'])
def fetch_trending():
    # Fetch and store trending articles
    limit = request.json.get('limit', 10) if request.json else 10
    
    try:
        saved_count, updated_count, failed_urls = article_service_instance.fetch_and_save_trending_articles(limit)
        return jsonify({
            'success': True,
            'saved': saved_count,
            'updated': updated_count,
            'failed_urls': failed_urls,
            'failed_count': len(failed_urls),
            'message': f'Successfully fetched trending articles (saved: {saved_count}, updated: {updated_count}, failed: {len(failed_urls)})'
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/articles/fetch/new', methods=['POST'])
def fetch_new():
    # Fetch and store new articles
    limit = request.json.get('limit', 10) if request.json else 10
    
    try:
        saved_count, updated_count, failed_urls = article_service_instance.fetch_and_save_new_articles(limit)
        return jsonify({
            'success': True,
            'saved': saved_count,
            'updated': updated_count,
            'failed_urls': failed_urls,
            'failed_count': len(failed_urls),
            'message': f'Successfully fetched new articles (saved: {saved_count}, updated: {updated_count}, failed: {len(failed_urls)})'
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/articles', methods=['GET'])
def get_articles():
    # Get articles with filtering, searching, and sorting
    try:
        # Parse query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        keyword = request.args.get('keyword', '').strip() or None
        author = request.args.get('author', '').strip() or None
        min_score = request.args.get('min_score', type=int)
        max_score = request.args.get('max_score', type=int)
        tag = request.args.get('tag', '').strip() or None
        start_date = request.args.get('start_date', '').strip() or None
        end_date = request.args.get('end_date', '').strip() or None
        sort_by = request.args.get('sort_by', 'score')
        order = request.args.get('order', 'desc')
        
        # Get articles from service
        result = article_service_instance.get_articles(
            page=page,
            per_page=per_page,
            keyword=keyword,
            author=author,
            min_score=min_score,
            max_score=max_score,
            tag=tag,
            start_date=start_date,
            end_date=end_date,
            sort_by=sort_by,
            order=order
        )
        
        return jsonify({
            'success': True,
            **result
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    # Get a specific article by ID
    try:
        article = article_service_instance.get_article_by_id(article_id)
        
        if not article:
            return jsonify({'success': False, 'error': 'Article not found'}), 404
        
        return jsonify({
            'success': True,
            'data': article.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/articles/trending', methods=['GET'])
def get_trending():
    # Get top trending articles from database
    try:
        limit = int(request.args.get('limit', 10))
        
        articles = article_service_instance.get_trending_articles(limit)
        
        return jsonify({
            'success': True,
            'data': [article.to_dict() for article in articles],
            'count': len(articles)
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/articles/stats', methods=['GET'])
def get_stats():
    # Get statistics about articles
    try:
        stats = article_service_instance.get_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

