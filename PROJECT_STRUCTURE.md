# Project Structure

This document describes the industry-standard folder structure for the HackerNews API project.

## Directory Structure

```
Bootcamp/
├── app/                          # Main application package
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuration settings
│   ├── models/                  # Database models
│   │   ├── __init__.py
│   │   └── article.py           # Article model
│   ├── database/                # Database connection
│   │   ├── __init__.py
│   │   └── connection.py         # Database class
│   ├── api/                     # API routes
│   │   ├── __init__.py
│   │   └── routes.py            # All API endpoints
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   ├── article_service.py   # Article business logic
│   │   └── hn_fetcher.py        # HackerNews API client
│   └── utils/                   # Utility functions
│       └── __init__.py
├── tests/                       # Test files
│   └── __init__.py
├── migrations/                  # Database migrations (future)
├── logs/                       # Log files
├── .env                        # Environment variables
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── SYSTEM_DESIGN.md            # System design document
├── run.py                      # Development entry point
└── wsgi.py                     # Production entry point (Gunicorn)
```

## File Descriptions

### Root Level Files

- **`run.py`** - Development server entry point
  - Usage: `python run.py`
  - Runs Flask development server with debug mode

- **`wsgi.py`** - Production WSGI entry point
  - Usage: `gunicorn wsgi:app`
  - For production deployment with Gunicorn

- **`requirements.txt`** - Python package dependencies

- **`.env`** - Environment variables (not in git)
  - Database URL, port, etc.

- **`.env.example`** - Template for environment variables

### App Package (`app/`)

- **`app/__init__.py`** - Application factory
  - Creates Flask app instance
  - Initializes database and routes

- **`app/config.py`** - Configuration classes
  - Development, Production, Testing configs

### Models (`app/models/`)

- **`app/models/article.py`** - Article database model
  - SQLAlchemy model definition
  - Table structure and relationships

### Database (`app/database/`)

- **`app/database/connection.py`** - Database connection manager
  - SQLAlchemy engine and session management

### API Routes (`app/api/`)

- **`app/api/routes.py`** - All REST API endpoints
  - Health check
  - Article fetching endpoints
  - Article query endpoints
  - Statistics endpoint

### Services (`app/services/`)

- **`app/services/article_service.py`** - Article business logic
  - Save/update articles
  - Fetch and save operations

- **`app/services/hn_fetcher.py`** - HackerNews API client
  - External API calls
  - Data fetching and processing
  - Tag extraction

### Utilities (`app/utils/`)

- **`app/utils/`** - Helper functions
  - Placeholder for future utility functions

### Tests (`tests/`)

- **`tests/`** - Unit and integration tests
  - Placeholder for test files

### Migrations (`migrations/`)

- **`migrations/`** - Database migrations
  - Placeholder for Alembic migrations

### Logs (`logs/`)

- **`logs/`** - Application logs
  - Log files directory

## Architecture Pattern

This structure follows the **Layered Architecture** pattern:

1. **Presentation Layer** (`app/api/`) - HTTP endpoints
2. **Business Logic Layer** (`app/services/`) - Business rules
3. **Data Access Layer** (`app/models/`, `app/database/`) - Database operations
4. **External Services** (`app/services/hn_fetcher.py`) - External API calls

## Benefits of This Structure

1. **Separation of Concerns** - Each layer has a specific responsibility
2. **Scalability** - Easy to add new features
3. **Maintainability** - Clear organization
4. **Testability** - Easy to write unit tests
5. **Industry Standard** - Follows Python/Flask best practices

## Running the Application

### Development
```bash
python run.py
```

### Production
```bash
gunicorn wsgi:app --bind 0.0.0.0:5000 --workers 4
```

## Import Examples

```python
# From models
from app.models import Article

# From services
from app.services import ArticleService

# From database
from app.database import Database

# From config
from app.config import config
```

