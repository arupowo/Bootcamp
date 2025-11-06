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
```

**Important:** Never commit `.env` to version control! It contains sensitive credentials.

**Alternative:** You can also set environment variables directly:
```bash
export DATABASE_URL="postgresql://hackernews_user:your_password@localhost:5432/hackernews"
export PORT=5000
```

### 4. Run the Application

```bash
python app.py
```

The API will be available at `http://localhost:5000`

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
├── app.py              # Main Flask application with REST API endpoints
├── database.py         # Database models and connection management
├── hn_fetcher.py       # HackerNews API fetching functions
├── api_fetch.py        # Original script (can be kept for reference)
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (create from .env.example)
├── .env.example        # Environment variables template
├── README.md           # This file
└── TUTORIAL.md         # Comprehensive tutorial
```

## Database Schema

The `articles` table contains:
- `id` - Primary key
- `hn_id` - HackerNews story ID (unique)
- `title` - Article title
- `url` - Article URL
- `hn_url` - HackerNews discussion URL
- `author` - Author username
- `score` - Article score/points
- `comment_count` - Number of comments
- `created_at` - When article was created on HN
- `fetched_at` - When article was fetched
- `tags` - JSON string of extracted tags/keywords

## Notes

- Articles are automatically tagged based on keywords in title and URL
- Duplicate articles (same `hn_id`) are updated instead of creating duplicates
- The API supports pagination for large result sets
- All endpoints return JSON responses

