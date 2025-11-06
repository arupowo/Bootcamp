from flask import Flask
from flask_cors import CORS
from app.config import config
from app.database.connection import Database
from app.api.routes import api_bp, init_routes


def create_app(config_name='default'):
    app = Flask(__name__)
    # Load configuration
    app.config.from_object(config[config_name])
    # Enable CORS
    CORS(app)
    # Initialize database
    db = Database(app.config['DATABASE_URL'])
    # Initialize routes with database
    init_routes(db)
    # Register blueprints
    app.register_blueprint(api_bp)
    # Store db in app context for access in routes
    app.db = db
    
    return app

