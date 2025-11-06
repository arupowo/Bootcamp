
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/hackernews'
    )
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('FLASK_ENV') == 'development'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    DATABASE_URL = os.getenv('TEST_DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/hackernews_test')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

