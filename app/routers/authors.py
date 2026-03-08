from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from app.database import get_db
from app.models.models import Book, Review
from app.auth import verify_api_key


router = APIRouter()

# NOTE: In your current models.py, Author is stored as a string field on Book
# (book.author) rather than a separate Author table. These endpoints query
# authors by grouping books — if you later add a separate Author model,
# these can be updated to use that table directly.


# ─── GET /authors ─────────────────────────────────────────────────────────────
# List all unique authors derived from the books table
@router.get("/")
def get_authors(
    search: Optional[str] = Query(None, description="Search by author name"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(Book.author, func.count(Book.id).label("book_count")) \
               .group_by(Book.author)

    if search:
        query = query.filter(Book.author.ilike(f"%{search}%"))

    total = query.count()
    results = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": [
            {"author": r.author, "book_count": r.book_count}
            for r in results
        ]
    }


# ─── GET /authors/{name}/books ────────────────────────────────────────────────
# Get all books by a specific author name
@router.get("/{author_name}/books")
def get_author_books(
    author_name: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    books = db.query(Book).filter(Book.author.ilike(f"%{author_name}%")) \
               .offset(offset).limit(limit).all()

    if not books:
        raise HTTPException(status_code=404, detail=f"No books found for author '{author_name}'")

    return {
        "author": author_name,
        "book_count": len(books),
        "books": [
            {"id": b.id, "title": b.title, "year": b.year_of_publication, "publisher": b.publisher}
            for b in books
        ]
    }


# ─── GET /authors/{name}/stats ────────────────────────────────────────────────
# Get analytics stats for a specific author — avg rating, total books, top book
@router.get("/{author_name}/stats")
def get_author_stats(author_name: str, db: Session = Depends(get_db)):
    # Check author exists
    books = db.query(Book).filter(Book.author.ilike(f"%{author_name}%")).all()

    if not books:
        raise HTTPException(status_code=404, detail=f"No books found for author '{author_name}'")

    book_ids = [b.id for b in books]

    # Average rating across all their books
    avg_rating = db.query(func.avg(Review.rating)) \
                   .filter(Review.book_id.in_(book_ids)) \
                   .scalar()

    # Total number of reviews
    total_reviews = db.query(func.count(Review.id)) \
                      .filter(Review.book_id.in_(book_ids)) \
                      .scalar()

    # Top rated book
    top_book = (
        db.query(Book, func.avg(Review.rating).label("avg"))
        .join(Review, Review.book_id == Book.id)
        .filter(Book.id.in_(book_ids))
        .group_by(Book.id)
        .order_by(func.avg(Review.rating).desc())
        .first()
    )

    return {
        "author": author_name,
        "total_books": len(books),
        "total_reviews": total_reviews,
        "avg_rating": round(avg_rating, 2) if avg_rating else None,
        "top_rated_book": {
            "title": top_book.Book.title,
            "avg_rating": round(top_book.avg, 2)
        } if top_book else None
    }