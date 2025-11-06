# HackerNews API - System Design Document

## Table of Contents
1. [System Overview](#system-overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Component Breakdown](#component-breakdown)
4. [Data Flow](#data-flow)
5. [User Flows](#user-flows)
6. [Database Schema](#database-schema)
7. [API Endpoints](#api-endpoints)
8. [Technology Stack](#technology-stack)

---

## System Overview

The HackerNews API is a RESTful web service that fetches articles from the HackerNews public API, stores them in a PostgreSQL database, and provides endpoints for querying, filtering, and retrieving article data.

### Key Features
- ✅ Fetch articles from HackerNews API (top, trending, new)
- ✅ Store articles in PostgreSQL database
- ✅ Query articles with filtering, searching, and sorting
- ✅ Pagination support
- ✅ Automatic tag extraction
- ✅ Statistics endpoint

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│  (Browser, Postman, Mobile App, Frontend Application)          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/REST API
                             │ (JSON Requests/Responses)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API LAYER (Flask)                          │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  app.py                                                    │ │
│  │  - Route Handlers                                          │ │
│  │  - Request Validation                                     │ │
│  │  - Response Formatting                                     │ │
│  │  - Error Handling                                         │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│   DATA FETCHING LAYER     │  │   DATABASE LAYER          │
│  ┌────────────────────┐  │  │  ┌────────────────────┐  │
│  │  hn_fetcher.py     │  │  │  │  database.py       │  │
│  │  - Fetch articles  │  │  │  │  - SQLAlchemy ORM   │  │
│  │  - Extract tags    │  │  │  │  - Article Model   │  │
│  │  - Process data    │  │  │  │  - Session Mgmt    │  │
│  └────────────────────┘  │  │  └────────────────────┘  │
└────────────┬──────────────┘  └────────────┬──────────────┘
             │                             │
             │ HTTP Requests               │ SQL Queries
             │                             │
             ▼                             ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│  EXTERNAL API            │  │  POSTGRESQL DATABASE     │
│  HackerNews Firebase API │  │  ┌────────────────────┐  │
│  - topstories.json       │  │  │  articles table   │  │
│  - newstories.json       │  │  │  - id             │  │
│  - item/{id}.json        │  │  │  - hn_id          │  │
│                          │  │  │  - title          │  │
│                          │  │  │  - score          │  │
│                          │  │  │  - author         │  │
│                          │  │  │  - tags           │  │
│                          │  │  │  - ...            │  │
│                          │  │  └────────────────────┘  │
└──────────────────────────┘  └──────────────────────────┘
```

---

## Component Breakdown

### 1. API Layer (`app.py`)

**Responsibility:** Handle HTTP requests and responses

**Components:**
- **Flask Application** - Web framework
- **Route Handlers** - 8 REST endpoints
- **Request Processing** - Parse query parameters, JSON body
- **Response Formatting** - Convert data to JSON
- **Error Handling** - Try/catch blocks, HTTP status codes

**Key Functions:**
- `save_articles_to_db()` - Save/update articles in database
- Route handlers for each endpoint

---

### 2. Data Fetching Layer (`hn_fetcher.py`)

**Responsibility:** Fetch and process data from HackerNews API

**Components:**
- **Story ID Fetchers** - Get lists of story IDs (top, new, best)
- **Story Detail Fetcher** - Get full story data by ID
- **Tag Extractor** - Extract keywords/tags from title and URL
- **Article Processor** - Transform HackerNews data to our format

**Key Functions:**
- `fetch_top_story_ids()` - Get top story IDs
- `fetch_story_details()` - Get story details
- `extract_tags()` - Extract tags from text
- `fetch_top_articles()` - Complete top articles fetch
- `fetch_trending_articles()` - Fetch trending articles
- `fetch_new_articles()` - Fetch new articles

---

### 3. Database Layer (`database.py`)

**Responsibility:** Database models and connection management

**Components:**
- **Article Model** - SQLAlchemy ORM model
- **Database Class** - Connection manager
- **Session Management** - Create and manage database sessions

**Key Components:**
- `Article` - Database model with columns and indexes
- `Database` - Engine and session factory
- `to_dict()` - Convert model to dictionary

---

### 4. External Services

**HackerNews Firebase API:**
- Public REST API
- No authentication required
- Rate limits: ~10 requests/second
- Endpoints:
  - `/v0/topstories.json` - Top story IDs
  - `/v0/newstories.json` - New story IDs
  - `/v0/item/{id}.json` - Story details

**PostgreSQL Database:**
- Relational database
- Stores article metadata
- Indexed for fast queries

---

## Data Flow

### Flow 1: Fetching and Storing Articles

```
1. Client Request
   POST /api/articles/fetch/top
   Body: {"limit": 10}
   │
   ▼
2. Flask Route Handler (app.py)
   - Receives request
   - Extracts limit parameter
   - Calls fetch_top_articles(10)
   │
   ▼
3. Data Fetching Layer (hn_fetcher.py)
   - Calls fetch_top_story_ids(10)
   - Gets: [12345, 12346, ...]
   │
   ▼
4. External API Call
   - For each ID: GET /v0/item/{id}.json
   - Receives story data
   │
   ▼
5. Data Processing
   - Extracts title, url, score, etc.
   - Calls extract_tags(title, url)
   - Formats as article dictionary
   │
   ▼
6. Database Storage (app.py)
   - Calls save_articles_to_db(articles)
   - Opens database session
   - For each article:
     - Check if exists (by hn_id)
     - Insert new OR update existing
   - Commit changes
   │
   ▼
7. Response
   - Returns JSON with success status
   - Includes saved/updated counts
```

### Flow 2: Querying Articles

```
1. Client Request
   GET /api/articles?keyword=python&min_score=100&page=1
   │
   ▼
2. Flask Route Handler (app.py)
   - Receives request
   - Parses query parameters
   - Opens database session
   │
   ▼
3. Query Building
   - Start: session.query(Article)
   - Add filter: .filter(Article.title.ilike('%python%'))
   - Add filter: .filter(Article.score >= 100)
   - Add sorting: .order_by(Article.score.desc())
   - Add pagination: .offset(0).limit(20)
   │
   ▼
4. Database Query (PostgreSQL)
   - Executes SQL query
   - Returns matching articles
   │
   ▼
5. Data Transformation
   - Convert Article objects to dictionaries
   - Add pagination metadata
   │
   ▼
6. Response
   - Returns JSON with articles and pagination info
```

---

## User Flows

### User Flow 1: Fetch Top Articles

```
┌─────────┐
│ Client  │
└────┬────┘
     │
     │ 1. POST /api/articles/fetch/top
     │    {"limit": 20}
     ▼
┌─────────────────┐
│  Flask API      │
│  (app.py)       │
└────┬────────────┘
     │
     │ 2. Call fetch_top_articles(20)
     ▼
┌─────────────────┐
│ hn_fetcher.py   │
└────┬────────────┘
     │
     │ 3. GET topstories.json
     ▼
┌─────────────────┐
│ HackerNews API  │
│ Returns IDs     │
└────┬────────────┘
     │
     │ 4. For each ID: GET item/{id}.json
     ▼
┌─────────────────┐
│ HackerNews API  │
│ Returns details │
└────┬────────────┘
     │
     │ 5. Process & extract tags
     ▼
┌─────────────────┐
│ Article Data    │
│ (List of dicts) │
└────┬────────────┘
     │
     │ 6. save_articles_to_db()
     ▼
┌─────────────────┐
│ PostgreSQL      │
│ Insert/Update   │
└────┬────────────┘
     │
     │ 7. Return success response
     ▼
┌─────────┐
│ Client  │
│ Receives│
│ Response│
└─────────┘
```

### User Flow 2: Search Articles

```
┌─────────┐
│ Client  │
└────┬────┘
     │
     │ 1. GET /api/articles?keyword=python&min_score=50
     ▼
┌─────────────────┐
│  Flask API      │
│  (app.py)       │
└────┬────────────┘
     │
     │ 2. Parse query parameters
     │    keyword = "python"
     │    min_score = 50
     ▼
┌─────────────────┐
│ Query Builder   │
│ - Filter by     │
│   keyword       │
│ - Filter by     │
│   score         │
│ - Sort &        │
│   paginate      │
└────┬────────────┘
     │
     │ 3. Execute SQL query
     ▼
┌─────────────────┐
│ PostgreSQL      │
│ SELECT articles │
│ WHERE ...       │
└────┬────────────┘
     │
     │ 4. Return Article objects
     ▼
┌─────────────────┐
│ Transform to    │
│ JSON            │
└────┬────────────┘
     │
     │ 5. Return response
     ▼
┌─────────┐
│ Client  │
│ Receives│
│ Articles│
└─────────┘
```

### User Flow 3: Get Trending Articles

```
┌─────────┐
│ Client  │
└────┬────┘
     │
     │ 1. GET /api/articles/trending?limit=10
     ▼
┌─────────────────┐
│  Flask API      │
│  (app.py)       │
└────┬────────────┘
     │
     │ 2. Query database
     │    ORDER BY score DESC
     │    LIMIT 10
     ▼
┌─────────────────┐
│ PostgreSQL      │
│ Query articles  │
│ table           │
└────┬────────────┘
     │
     │ 3. Return top articles
     ▼
┌─────────────────┐
│ Transform &     │
│ Return JSON     │
└────┬────────────┘
     │
     │ 4. Response
     ▼
┌─────────┐
│ Client  │
│ Receives│
│ Trending│
│ Articles│
└─────────┘
```

---

## Database Schema

### Articles Table

```
┌─────────────────────────────────────────────────────────┐
│                    articles                              │
├─────────────────────────────────────────────────────────┤
│ id              INTEGER (PK, Auto-increment)            │
│ hn_id           INTEGER (Unique, Indexed)               │
│ title           VARCHAR(500) (Indexed)                  │
│ url             TEXT                                    │
│ hn_url          TEXT                                    │
│ author          VARCHAR(100) (Indexed)                 │
│ score           INTEGER (Indexed, Default: 0)           │
│ comment_count   INTEGER (Default: 0)                    │
│ created_at      TIMESTAMP (Indexed)                     │
│ fetched_at      TIMESTAMP                                │
│ tags            TEXT (JSON string)                      │
└─────────────────────────────────────────────────────────┘

Indexes:
- Primary Key: id
- Unique Index: hn_id
- Indexes: title, author, score, created_at
- Composite Index: (score, created_at)
```

### Relationships

Currently, the system uses a single table design. Each article is independent.

---

## API Endpoints

### Fetch Endpoints (POST)

| Endpoint | Method | Description | Functions Used |
|----------|--------|-------------|----------------|
| `/api/articles/fetch/top` | POST | Fetch top articles | `fetch_top_articles()`, `save_articles_to_db()` |
| `/api/articles/fetch/trending` | POST | Fetch trending articles | `fetch_trending_articles()`, `save_articles_to_db()` |
| `/api/articles/fetch/new` | POST | Fetch new articles | `fetch_new_articles()`, `save_articles_to_db()` |

### Query Endpoints (GET)

| Endpoint | Method | Description | Functions Used |
|----------|--------|-------------|----------------|
| `/api/articles` | GET | Query articles with filters | `db.get_session()`, `session.query()`, `article.to_dict()` |
| `/api/articles/<id>` | GET | Get specific article | `session.query().filter_by()`, `article.to_dict()` |
| `/api/articles/trending` | GET | Get trending from DB | `session.query().order_by()`, `article.to_dict()` |
| `/api/articles/stats` | GET | Get statistics | `session.query().count()`, `func.avg()`, `func.max()`, `func.sum()` |
| `/api/health` | GET | Health check | None (direct response) |

---

## Technology Stack

### Backend Framework
- **Flask** - Python web framework
- **Flask-CORS** - Cross-origin resource sharing

### Database
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM (Object-Relational Mapping)
- **psycopg2** - PostgreSQL adapter

### External APIs
- **HackerNews Firebase API** - Public REST API

### Utilities
- **python-dotenv** - Environment variable management
- **requests** - HTTP library for API calls

### Development
- **Python 3.x** - Programming language

---

## System Characteristics

### Scalability
- **Current:** Single server, single database
- **Limitations:** Sequential API calls, N+1 queries
- **Potential:** Can scale horizontally with load balancer

### Performance
- **Database:** Indexed for fast queries
- **Caching:** Not implemented (can add Redis)
- **API Calls:** Sequential (can parallelize)

### Reliability
- **Error Handling:** Try/catch blocks in place
- **Database:** Transaction support (commit/rollback)
- **External API:** Timeout handling (10 seconds)

### Security
- **SQL Injection:** Prevented by SQLAlchemy ORM
- **CORS:** Enabled (can be restricted)
- **Input Validation:** Basic (can be enhanced)

---

## Data Flow Summary

```
External API → Fetch Layer → Process → Database → Query Layer → API → Client
     ↓              ↓           ↓          ↓           ↓         ↓       ↓
HackerNews    hn_fetcher   Extract   PostgreSQL   SQLAlchemy  Flask   JSON
Firebase      .py          Tags      Database     ORM         app.py  Response
```

---

## Key Design Decisions

1. **Single Table Design** - All articles in one table (simple, sufficient for current needs)

2. **Tag Storage** - JSON string in TEXT column (simple, but could use JSONB for better querying)

3. **Update Strategy** - Check existence by `hn_id`, then insert or update (prevents duplicates)

4. **Pagination** - Offset/limit based (works well for moderate data sizes)

5. **Error Handling** - Try/catch with rollback (ensures data consistency)

6. **Session Management** - One session per request (isolation, safety)

---

## Future Enhancements

1. **Caching Layer** - Redis for frequently accessed data
2. **Parallel Fetching** - Concurrent requests to HackerNews API
3. **Bulk Operations** - Optimize database inserts/updates
4. **Full-text Search** - PostgreSQL full-text search for better searching
5. **Rate Limiting** - Protect API from abuse
6. **Authentication** - API keys for protected endpoints
7. **Background Jobs** - Celery for async article fetching
8. **Monitoring** - Logging and metrics collection

---

## Conclusion

The current system implements a clean three-tier architecture:
- **Presentation Layer** (Flask API)
- **Business Logic Layer** (Data fetching and processing)
- **Data Layer** (PostgreSQL database)

The design is modular, maintainable, and provides a solid foundation for future enhancements.

