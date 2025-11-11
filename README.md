# HackerNews AI Article Assistant

An intelligent article management system that fetches HackerNews articles, processes them with AI, and provides natural language search through a RAG (Retrieval-Augmented Generation) interface.

## 🚀 How to Run

### Prerequisites
- Python 3.12+
- PostgreSQL with pgvector extension
- Google Gemini API key

### 1. Database Setup

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database and enable pgvector
sudo -u postgres psql
CREATE DATABASE hackernews;
CREATE USER hackernews_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE hackernews TO hackernews_user;
\c hackernews
CREATE EXTENSION vector;
\q
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file:

```bash
# Database
DATABASE_URL=postgresql://hackernews_user:your_password@localhost:5432/hackernews

# Flask API
PORT=5000
FLASK_ENV=development

# Google Gemini API (Required for AI features)
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional
API_BASE_URL=http://localhost:5000/api
```

Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

### 4. Start the Application

**Option A: Flask API + RAG Chat Interface (Recommended)**

```bash
# Terminal 1: Start Flask API
python run.py

# Terminal 2: Start RAG Chat UI
streamlit run streamlit_rag.py
```

**Option B: Flask API + LangChain Agent Interface**

```bash
# Terminal 1: Start Flask API
python run.py

# Terminal 2: Start Agent Chat UI
streamlit run streamlit_app.py
```

- Flask API: `http://localhost:5000`
- Streamlit UI: `http://localhost:8501`

---

## 🏗️ Architecture

### Tech Stack

**Backend**
- **Flask 3.1.0** - REST API framework
- **SQLAlchemy 2.0.36** - ORM for database operations
- **PostgreSQL + pgvector** - Vector database for embeddings
- **psycopg2** - PostgreSQL adapter

**AI/ML**
- **Google Gemini 2.5 Flash** - Large Language Model
- **LangChain 0.3.13** - Agent framework and tooling
- **Groq (text-embedding-3-small)** - Text embeddings generation
- **tiktoken** - Token counting
- **newspaper3k** - Article scraping

**UI**
- **Streamlit 1.40.1** - Web interface for chat

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit UI Layer                     │
│  ┌──────────────────────┐      ┌─────────────────────────┐ │
│  │  streamlit_rag.py    │      │  streamlit_app.py       │ │
│  │  (RAG Interface)     │      │  (Agent Interface)      │ │
│  └──────────────────────┘      └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer (AI)                       │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐  │
│  │ RAG Service  │  │ Embedding   │  │ Summary Service  │  │
│  │              │  │ Service     │  │                  │  │
│  └──────────────┘  └─────────────┘  └──────────────────┘  │
│  ┌──────────────┐  ┌─────────────┐                        │
│  │ Chunking     │  │ LangChain   │                        │
│  │ Service      │  │ Tools       │                        │
│  └──────────────┘  └─────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Flask REST API Layer                     │
│               /api/articles/*, /api/health                  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer (Data)                     │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐  │
│  │ Article      │  │ Scraping    │  │ HackerNews       │  │
│  │ Service      │  │ Service     │  │ Fetcher          │  │
│  └──────────────┘  └─────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Database Layer                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  PostgreSQL + pgvector                               │  │
│  │  - articles table (metadata, content, summary)       │  │
│  │  - article_chunks table (embeddings, headers)        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

**articles table**
- Stores HackerNews article metadata and scraped content
- Fields: `id`, `hn_id`, `title`, `url`, `author`, `score`, `comment_count`, `created_at`, `tags`, `content`, `summary`
- Indexes: `hn_id` (unique), composite index on `(score, created_at)`

**article_chunks table**
- Stores chunked article content with vector embeddings
- Fields: `id`, `article_id`, `chunk_text`, `chunk_type` (header/content), `chunk_index`, `embedding` (1536-dim vector), `token_count`, `created_at`
- Indexes: `article_id`, `chunk_type`
- Vector search using pgvector cosine similarity

### Processing Pipeline

1. **Fetch** → Articles fetched from HackerNews API
2. **Scrape** → Full article content scraped using newspaper3k
3. **Chunk** → Content split into headers and body chunks
4. **Embed** → Text converted to 1536-dim vectors (Groq embeddings)
5. **Store** → Saved to PostgreSQL with metadata
6. **Retrieve** → RAG service searches using cosine similarity
7. **Generate** → LLM generates response with retrieved context

---

## ✨ Features

### Core Features

1. **HackerNews Integration**
   - Fetch top, trending, and new articles from HackerNews API
   - Automatic deduplication using upsert logic
   - Metadata extraction (title, author, score, comments)

2. **Intelligent Article Scraping**
   - Full content extraction from source URLs
   - Automatic keyword/tag extraction (30+ tech keywords)
   - Failure handling for unreachable URLs

3. **AI-Powered Summarization**
   - Automatic article summaries using Gemini LLM
   - Summary storage for quick reference

4. **Advanced Chunking System**
   - Separates headers from content
   - Token-based chunking (max 512 tokens/chunk)
   - Maintains context integrity

5. **Vector Search with RAG**
   - 1536-dimensional embeddings (Groq text-embedding-3-small)
   - Cosine similarity search using pgvector
   - Retrieves top-K most relevant chunks
   - Context-aware responses with source citations

6. **REST API**
   - 8 RESTful endpoints
   - Advanced filtering (keyword, author, score, tags)
   - Pagination support
   - Sorting by score, date, comment count

7. **Dual Chat Interfaces**
   - **RAG Interface** (`streamlit_rag.py`): Direct semantic search + LLM
   - **Agent Interface** (`streamlit_app.py`): LangChain agents with tools
   - Real-time URL embedding in responses
   - Conversation memory
   - Modern responsive UI

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/articles/fetch/top` | Fetch top articles from HN |
| POST | `/api/articles/fetch/trending` | Fetch trending articles |
| POST | `/api/articles/fetch/new` | Fetch new articles |
| GET | `/api/articles` | List articles with filters |
| GET | `/api/articles/<id>` | Get specific article |
| GET | `/api/articles/trending` | Get trending from DB |
| GET | `/api/articles/stats` | Database statistics |

---

## 📚 Examples

### 1. Fetch and Store Articles

```bash
# Fetch top 20 articles from HackerNews
curl -X POST http://localhost:5000/api/articles/fetch/top \
  -H "Content-Type: application/json" \
  -d '{"limit": 20}'

# Response
{
  "success": true,
  "saved": 15,
  "updated": 5,
  "failed_count": 0,
  "message": "Successfully fetched articles"
}
```

### 2. Search Articles by Keyword

```bash
# Find Python articles with score > 100
curl "http://localhost:5000/api/articles?keyword=python&min_score=100&sort_by=score&order=desc"

# Response
{
  "success": true,
  "data": [
    {
      "id": 1,
      "hn_id": 39234567,
      "title": "Python 3.13 Released",
      "url": "https://...",
      "author": "guido",
      "score": 245,
      "comment_count": 89,
      "created_at": "2025-11-10T12:30:00",
      "tags": "python,programming,release"
    }
  ],
  "total": 15,
  "page": 1,
  "per_page": 20
}
```

### 3. Filter by Tags

```bash
# Get AI-related articles
curl "http://localhost:5000/api/articles?tag=ai&sort_by=score&order=desc&per_page=10"
```

### 4. Get Statistics

```bash
curl "http://localhost:5000/api/articles/stats"

# Response
{
  "success": true,
  "stats": {
    "total_articles": 1523,
    "total_authors": 456,
    "avg_score": 78.5,
    "top_tags": ["python", "javascript", "ai", "security"]
  }
}
```

### 5. RAG Chat Interface (Streamlit)

**Example Queries:**

```
User: "What are the latest articles about AI?"
→ RAG searches embeddings, retrieves relevant headers, generates contextual response

User: "Summarize the article about Python 3.13"
→ Finds article, provides summary with source URL

User: "Show me trending articles with high scores"
→ Retrieves and ranks articles, embeds links in response
```

**Features in Chat:**
- Retrieved context shown in sidebar (top 4 articles)
- Embedded article previews with iframes
- Suggested follow-up questions
- Conversation memory across messages

### 6. LangChain Agent Interface

**Available Tools:**
- `fetch_top_articles`: Fetch from HackerNews
- `search_articles`: Search database with filters
- `get_article_details`: Get specific article info
- `get_trending_articles`: Query trending articles
- `get_statistics`: Database stats

**Example:**
```
User: "Fetch 10 articles and show me those about machine learning"
Agent: [Uses fetch_top_articles] → [Uses search_articles] → Provides filtered results
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `GOOGLE_API_KEY` | Yes | - | Gemini API key for LLM |
| `PORT` | No | 5000 | Flask server port |
| `FLASK_ENV` | No | development | Flask environment |
| `API_BASE_URL` | No | http://localhost:5000/api | API base URL for tools |

### Key Features Configuration

- **Chunking**: Max 512 tokens per chunk (configurable in `chunking_services.py`)
- **Embeddings**: 1536 dimensions, Groq text-embedding-3-small model
- **RAG Retrieval**: Top-K = 4 relevant chunks (configurable in `rag_service.py`)
- **LLM**: Gemini 2.5 Flash, temperature = 0.7

---

## 📂 Project Structure

```
Bootcamp/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── config.py             # Environment configuration
│   ├── api/
│   │   └── routes.py         # REST API endpoints
│   ├── database/
│   │   └── connection.py     # Database connection & session management
│   ├── models/
│   │   ├── article.py        # Article ORM model
│   │   └── article_chunk.py  # Chunk model with vector embeddings
│   ├── services/
│   │   ├── article_service.py    # Article CRUD operations
│   │   ├── hn_fetcher.py         # HackerNews API integration
│   │   ├── scraping_service.py   # Web scraping
│   │   ├── chunking_services.py  # Text chunking
│   │   ├── embedding_service.py  # Vector embeddings
│   │   ├── summary_service.py    # Article summarization
│   │   ├── rag_service.py        # RAG pipeline
│   │   └── ui_helper.py          # Streamlit UI utilities
│   └── utils/
│       ├── api_client.py         # HTTP client for API calls
│       └── tools.py              # LangChain tools
├── run.py                    # Flask development server
├── streamlit_app.py          # LangChain agent chat UI
├── streamlit_rag.py          # RAG chat UI (recommended)
├── requirements.txt          # Python dependencies
└── README.md
```

---

Built with ❤️ by Arup | Jeavio Bootcamp
