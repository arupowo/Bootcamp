# HackerNews API - REST API with PostgreSQL Database

A comprehensive REST API for fetching, storing, and querying HackerNews articles with PostgreSQL support.

## Features

- ✅ Fetch top & trending Hacker News articles
- ✅ Store articles in PostgreSQL database
- ✅ Filter & search articles based on tags, keywords, and score
- ✅ REST API to query, filter, and sort articles
- ✅ Endpoints to retrieve top trending posts
- ✅ Pagination support
- ✅ Search functionality
- ✅ **NEW:** Streamlit Chat UI with Gemini LLM for natural language article browsing and summarization

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. PostgreSQL Setup

```bash
# Install PostgreSQL (if not installed)
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE hackernews;
CREATE USER hackernews_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE hackernews TO hackernews_user;
\q
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```bash
# Database Configuration
DATABASE_URL=postgresql://hackernews_user:your_password@localhost:5432/hackernews

# Flask Configuration
PORT=5000
FLASK_ENV=development

# Google Gemini API (Required for Streamlit Chat UI)
GOOGLE_API_KEY=your_gemini_api_key_here

# API Base URL (Optional, defaults to http://localhost:5000/api)
API_BASE_URL=http://localhost:5000/api
```

**Get Gemini API Key:** Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to create an API key.

**Important:** Never commit `.env` to version control! It contains sensitive credentials.

**Alternative:** You can also set environment variables directly:
```bash
export DATABASE_URL="postgresql://hackernews_user:your_password@localhost:5432/hackernews"
export PORT=5000
```

### 4. Run the Flask API

```bash
python run.py
```

The API will be available at `http://localhost:5000`

### 5. Run the Streamlit Chat UI (Optional)

```bash
# Make sure you have GOOGLE_API_KEY in your .env file
streamlit run streamlit_app.py
```

The Streamlit app will open at `http://localhost:8501`

### AI Chat Interface Features

The Streamlit chat interface provides natural language interaction with your article database:

**Example Queries:**
- "Fetch the top 10 articles from HackerNews"
- "Search for articles about Python"
- "Show me trending articles"
- "What are the statistics?"
- "Find articles with score above 100"

**Capabilities:**
- 7 LangChain tools for article operations
- Conversation memory (remembers previous context)
- Automatic tool selection based on user queries
- Natural language summarization

## API Endpoints

### Health Check
```
GET /api/health
```

### Fetch Articles

#### Fetch Top Articles
```
POST /api/articles/fetch/top
Body: {"limit": 10}
```

#### Fetch Trending Articles
```
POST /api/articles/fetch/trending
Body: {"limit": 10}
```

#### Fetch New Articles
```
POST /api/articles/fetch/new
Body: {"limit": 10}
```

### Query Articles

#### Get All Articles (with filtering, searching, sorting)
```
GET /api/articles?keyword=python&min_score=100&sort_by=score&order=desc&page=1&per_page=20
```

**Query Parameters:**
- `keyword` - Search in article titles
- `author` - Filter by author name
- `min_score` - Minimum score filter
- `max_score` - Maximum score filter
- `tag` - Filter by tag/keyword in tags
- `sort_by` - Sort by: `score`, `created_at`, `comment_count`
- `order` - Order: `asc` or `desc`
- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 20)

#### Get Specific Article
```
GET /api/articles/<id>
```

#### Get Trending Articles
```
GET /api/articles/trending?limit=10
```

#### Get Statistics
```
GET /api/articles/stats
```

## Example Usage

### Fetch and Store Top Articles
```bash
curl -X POST http://localhost:5000/api/articles/fetch/top \
  -H "Content-Type: application/json" \
  -d '{"limit": 20}'
```

### Search Articles
```bash
curl "http://localhost:5000/api/articles?keyword=python&min_score=50&sort_by=score&order=desc"
```

### Get Trending Articles
```bash
curl "http://localhost:5000/api/articles/trending?limit=10"
```

### Filter by Author
```bash
curl "http://localhost:5000/api/articles?author=pg&min_score=100"
```

### Filter by Tag
```bash
curl "http://localhost:5000/api/articles?tag=ai&sort_by=score&order=desc"
```

## Project Structure

```
.
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                 # Configuration management
│   ├── api/
│   │   └── routes.py            # REST API endpoints (8 routes)
│   ├── services/
│   │   ├── article_service.py   # Business logic layer
│   │   └── hn_fetcher.py        # HackerNews API integration
│   ├── models/
│   │   └── article.py           # SQLAlchemy model
│   ├── database/
│   │   └── connection.py        # Database connection manager
│   └── utils/
│       ├── api_client.py        # HTTP client for API calls
│       └── tools.py              # LangChain tools (7 tools)
├── run.py                        # Development server entry point
├── wsgi.py                       # Production WSGI entry point
├── streamlit_app.py              # AI Chat UI
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (not in git)
└── README.md                     # This file
```

## Database Schema

The `articles` table contains:
- `id` - Primary key (auto-increment)
- `hn_id` - HackerNews story ID (unique, indexed)
- `title` - Article title (indexed for search)
- `url` - Article URL
- `hn_url` - HackerNews discussion URL
- `author` - Author username (indexed)
- `score` - Article score/points (indexed)
- `comment_count` - Number of comments
- `created_at` - When article was created on HN (indexed)
- `fetched_at` - When article was fetched
- `tags` - JSON string of extracted tags/keywords

**Indexes:**
- Single column indexes on: `hn_id`, `title`, `author`, `score`, `created_at`
- Composite index on: `(score, created_at)` for trending queries

## Technology Stack

**Backend:**
- Flask 3.0.0 - REST API framework
- SQLAlchemy 2.0.23 - ORM
- PostgreSQL - Database
- Python 3.12+

**AI/ML:**
- LangChain 0.1.0 - Agent framework
- Google Gemini 2.5 Flash - LLM
- Streamlit 1.29.0 - Chat UI
- Pydantic 2.5.0 - Data validation

## Key Features

- **Upsert Logic** - Updates existing articles, inserts new ones (prevents duplicates)
- **Automatic Tagging** - Extracts 30+ tech keywords from titles/URLs
- **Layered Architecture** - Separation of routes, services, models
- **Error Handling** - Comprehensive try/catch with rollback
- **Production Ready** - Gunicorn WSGI support included

## Notes

- Articles are automatically tagged based on keywords in title and URL
- Duplicate articles (same `hn_id`) are updated instead of creating duplicates
- The API supports pagination for large result sets
- All endpoints return JSON responses
- CORS enabled for frontend integration

