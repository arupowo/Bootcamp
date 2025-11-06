
from app import create_app

if __name__ == '__main__':
    app = create_app(config_name='development')
    app.db.create_tables()
    
    print(f"Starting HackerNews API on http://0.0.0.0:{app.config['PORT']}")
    print(f"Using database: {app.config['DATABASE_URL'].split('@')[1] if '@' in app.config['DATABASE_URL'] else 'postgresql'}")
    
    app.run(debug=True, host='0.0.0.0', port=app.config['PORT'])

