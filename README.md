# BookVault API

A RESTful API for book discovery, reviews, and analytics.

BookVault integrates the Goodreads Books dataset (Soumik version, Kaggle) with a user-generated review system, providing endpoints for browsing books, managing reviews, and exploring analytics. The API uses a two-tier rating architecture: dataset ratings from the Goodreads community for large-scale analytics, and user review ratings computed live for personalised recommendations.

## Tech Stack

- **Framework:** FastAPI (Python)
- **Database:** SQLite via SQLAlchemy ORM
- **Authentication:** API key via `X-API-Key` header
- **Dataset:** Goodreads Books dataset (~11,000 books)
- **Testing:** pytest with FastAPI TestClient

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/bookvault-api.git
cd bookvault-api
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Import the dataset

```bash
python data/import_data.py
```

This loads the Goodreads CSV into `bookvault.db`.

### 4. Run the API

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### 5. Run tests

```bash
pip install pytest httpx
pytest tests/test_api.py -v
```

## API Documentation

Interactive Swagger documentation is available at `/docs` when the API is running:

```
http://127.0.0.1:8000/docs
https://bookvault-api-wth1.onrender.com/docs
```

A PDF export of the API documentation is available at [`docs/api_documentation.pdf`](docs/api_documentation.pdf).

## Authentication

Write endpoints (POST, PUT, DELETE) and the user listing endpoint require an `X-API-Key` header. 
All other GET endpoints are publicly accessible.

To authenticate, include the following header in your request:
```
X-API-Key: your-api-key-here
```

In Swagger UI, click the **Authorize** button at the top of the page and enter your API key.

If no `.env` file is present, the API defaults to the development key `bookvault-dev-key-123`.

## Error Codes

| Status Code | Meaning | Example |
|-------------|---------|---------|
| 200 | Success | Successful GET, PUT, or DELETE request |
| 201 | Created | Resource successfully created via POST |
| 401 | Unauthorized | Missing `X-API-Key` header on a protected endpoint |
| 403 | Forbidden | Invalid API key provided |
| 404 | Not Found | Requested resource does not exist (e.g. book ID not in database) |
| 409 | Conflict | Duplicate resource (e.g. username already taken, user already reviewed this book) |
| 422 | Unprocessable Entity | Request body fails validation (e.g. missing required field, rating out of range) |

## Endpoints Overview

### Books
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/books/` | List and search books (by title, author, or year) |
| GET | `/books/{id}` | Get a single book by ID |
| GET | `/books/top-rated` | Books ranked by user review average |
| GET | `/books/recommendations` | Recommended books above a rating threshold |
| POST | `/books/` | Create a new book (requires API key) |
| PUT | `/books/{id}` | Update a book (requires API key) |
| DELETE | `/books/{id}` | Delete a book (requires API key) |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/` | List all users (requires API key) |
| GET | `/users/{id}` | Get a user by ID |
| POST | `/users/` | Create a new user (requires API key) |
| PUT | `/users/{id}` | Update a user (requires API key) |
| DELETE | `/users/{id}` | Delete a user (requires API key) |

### Reviews
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reviews/` | List reviews (filter by book, user, or rating) |
| GET | `/reviews/{id}` | Get a single review |
| POST | `/reviews/` | Submit a review (requires API key) |
| PUT | `/reviews/{id}` | Update a review (requires API key) |
| DELETE | `/reviews/{id}` | Delete a review (requires API key) |

### Authors
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/authors/` | List all authors (derived from books) |
| GET | `/authors/{name}/books` | Get all books by an author |
| GET | `/authors/{name}/stats` | Author analytics (avg rating, top book) |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/summary` | Dataset overview statistics |
| GET | `/analytics/rating-distribution` | Rating distribution breakdown |
| GET | `/analytics/top-publishers` | Top publishers by average rating |
| GET | `/analytics/most-rated` | Most rated books by ratings count |
| GET | `/analytics/language-breakdown` | Books grouped by language |

## Project Structure

```
bookvault-api/
├── app/
│   ├── main.py              # FastAPI app, router registration, OpenAPI config
│   ├── database.py          # SQLAlchemy engine and session setup
│   ├── auth.py              # API key authentication dependency
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── models/
│   │   └── models.py        # SQLAlchemy ORM models (Book, User, Review, Like)
│   └── routers/
│       ├── books.py          # Books CRUD + recommendations + top-rated
│       ├── users.py          # Users CRUD
│       ├── reviews.py        # Reviews CRUD with validation
│       ├── authors.py        # Author endpoints (derived from books)
│       └── analytics.py      # Dataset analytics endpoints
├── data/
│   ├── books.csv             # Goodreads dataset
│   └── import_data.py        # CSV import script
├── tests/
│   └── test_api.py           # pytest test suite
├── docs/
│   └── api_documentation.pdf # Exported Swagger documentation
├── requirements.txt
└── README.md
```

## Dataset

The API uses the [Goodreads Books dataset](https://www.kaggle.com/datasets/jealousleopard/goodreadsbooks) by Soumik from Kaggle. It contains approximately 11,000 books with fields including title, authors, average rating, ISBN, language, page count, ratings count, publication date, and publisher.

## Testing

The test suite uses pytest with FastAPI's TestClient and a separate SQLite test database so that tests never affect production data. Tests cover all CRUD operations, authentication (no key, wrong key, valid key), pagination, search, input validation, and edge cases. Run with:

```bash
pytest tests/test_api.py -v
```

## API Documentation

Full API documentation is available in [api_documentation.pdf](api_documentation.pdf).

