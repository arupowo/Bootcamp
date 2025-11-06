
from app import create_app

app = create_app(config_name='production')

if __name__ == '__main__':
    app.db.create_tables()
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=app.config['DEBUG'])

