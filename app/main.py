from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.database import engine
from app.models.models import Base
from app.routers import books, genres, reviews, authors

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BookVault API",
    description="""
A RESTful API for book discovery, reviews, and analytics.

## Authentication
Write endpoints (POST, PUT, DELETE) require an **X-API-Key** header.
Read endpoints (GET) are publicly accessible.

## Endpoints
- **Books** — full CRUD + recommendations + top-rated
- **Authors** — browse authors and view stats
- **Genres** — manage and browse genres
- **Reviews** — create and manage book reviews
- **Analytics** — genre trends, rating distribution, leaderboards
    """,
    version="1.0.0",
)

app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(genres.router, prefix="/genres", tags=["Genres"])
app.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
app.include_router(authors.router, prefix="/authors", tags=["Authors"])

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to BookVault API",
        "docs": "/docs",
        "version": "1.0.0"
    }

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Register the API key security scheme
    schema.setdefault("components", {})
    schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }

    # Apply security to all non-GET operations
    for path in schema.get("paths", {}).values():
        for method, operation in path.items():
            if method in ("post", "put", "delete", "patch"):
                operation["security"] = [{"ApiKeyAuth": []}]

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi