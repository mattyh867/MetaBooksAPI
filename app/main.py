from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.database import engine
from app.models.models import Base
from app.routers import books, reviews, authors, analytics, users

# ─── Create tables on startup ─────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ─── App instance ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="BookVault API",
    description="""
A RESTful API for book discovery, reviews, and analytics powered by the Goodreads dataset.

## Authentication
Write endpoints (POST, PUT, DELETE) require an API key header.
Read endpoints (GET) are publicly accessible.

## Endpoints
- **Books** — full CRUD, search, filtering, recommendations, top-rated
- **Authors** — browse authors, view per-author stats
- **Reviews** — create and manage user reviews
- **Analytics** — rating distribution, publisher rankings, publication trends, language breakdown
    """,
    version="1.0.0",
)

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(books.router,     prefix="/books",     tags=["Books"])
app.include_router(authors.router,   prefix="/authors",   tags=["Authors"])
app.include_router(reviews.router,   prefix="/reviews",   tags=["Reviews"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(users.router,    prefix="/users",    tags=["Users"])


# ─── Root ─────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to BookVault API",
        "docs": "/docs",
        "version": "1.0.0",
        "endpoints": ["/books", "/authors", "/reviews", "/analytics"]
    }


# ─── Custom OpenAPI schema (adds Authorize button to Swagger UI) ──────────────
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi