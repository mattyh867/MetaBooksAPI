from fastapi import APIRouter, Depends, HTTPException, Query, Security
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional

from app.database import get_db
from app.models.models import Book, Genre, Review
from app.auth import verify_api_key

router = APIRouter()


# ─── GET /books ───────────────────────────────────────────────────────────────
# PUBLIC — no auth required
@router.get("/")
def get_books(
    search: Optional[str] = Query(None, description="Search by title or author"),
    genre: Optional[str] = Query(None, description="Filter by genre name"),
    year: Optional[int] = Query(None, description="Filter by year of publication"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(Book)

    if search:
        query = query.filter(
            or_(
                Book.title.ilike(f"%{search}%"),
                Book.author.ilike(f"%{search}%")
            )
        )
    if genre:
        query = query.join(Book.genres).filter(Genre.name.ilike(f"%{genre}%"))
    if year:
        query = query.filter(Book.year_of_publication == str(year))

    total = query.count()
    books = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": [format_book(b) for b in books]
    }


# ─── GET /books/top-rated ─────────────────────────────────────────────────────
# PUBLIC — no auth required
@router.get("/top-rated")
def top_rated_books(
    limit: int = Query(10, ge=1, le=50),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    db: Session = Depends(get_db)
):
    query = (
        db.query(Book, func.avg(Review.rating).label("avg_rating"), func.count(Review.id).label("review_count"))
        .join(Review, Review.book_id == Book.id)
        .group_by(Book.id)
        .order_by(func.avg(Review.rating).desc())
    )
    if genre:
        query = query.join(Book.genres).filter(Genre.name.ilike(f"%{genre}%"))

    results = query.limit(limit).all()
    return [
        {
            "title": r.Book.title,
            "author": r.Book.author,
            "avg_rating": round(r.avg_rating, 2),
            "review_count": r.review_count
        }
        for r in results
    ]


# ─── GET /books/recommendations ───────────────────────────────────────────────
# PUBLIC — no auth required
@router.get("/recommendations")
def get_recommendations(
    genre: Optional[str] = Query(None, description="Filter by genre"),
    rating_min: float = Query(4.0, ge=1.0, le=10.0, description="Minimum average rating"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    query = (
        db.query(Book, func.avg(Review.rating).label("avg_rating"))
        .join(Review, Review.book_id == Book.id)
        .group_by(Book.id)
        .having(func.avg(Review.rating) >= rating_min)
        .order_by(func.avg(Review.rating).desc())
    )
    if genre:
        query = query.join(Book.genres).filter(Genre.name.ilike(f"%{genre}%"))

    results = query.limit(limit).all()

    if not results:
        raise HTTPException(status_code=404, detail="No recommendations found for the given filters")

    return {
        "filters": {"genre": genre, "rating_min": rating_min},
        "count": len(results),
        "recommendations": [
            {"title": r.Book.title, "author": r.Book.author, "avg_rating": round(r.avg_rating, 2)}
            for r in results
        ]
    }


# ─── GET /books/{id} ──────────────────────────────────────────────────────────
# PUBLIC — no auth required
@router.get("/{book_id}")
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    return format_book(book)


# ─── POST /books ──────────────────────────────────────────────────────────────
# PROTECTED — requires X-API-Key header
@router.post("/", status_code=201, dependencies=[Depends(verify_api_key)])
def create_book(payload: dict, db: Session = Depends(get_db)):
    genre_ids = payload.pop("genre_ids", [])
    book = Book(**payload)

    if genre_ids:
        genres = db.query(Genre).filter(Genre.id.in_(genre_ids)).all()
        if len(genres) != len(genre_ids):
            raise HTTPException(status_code=404, detail="One or more genre IDs not found")
        book.genres = genres

    db.add(book)
    db.commit()
    db.refresh(book)

    return {"message": "Book created successfully", "book": format_book(book)}


# ─── PUT /books/{id} ──────────────────────────────────────────────────────────
# PROTECTED — requires X-API-Key header
@router.put("/{book_id}", dependencies=[Depends(verify_api_key)])
def update_book(book_id: int, payload: dict, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")

    genre_ids = payload.pop("genre_ids", None)
    if genre_ids is not None:
        genres = db.query(Genre).filter(Genre.id.in_(genre_ids)).all()
        book.genres = genres

    for field, value in payload.items():
        if hasattr(book, field):
            setattr(book, field, value)

    db.commit()
    db.refresh(book)

    return {"message": "Book updated successfully", "book": format_book(book)}


# ─── DELETE /books/{id} ───────────────────────────────────────────────────────
# PROTECTED — requires X-API-Key header
@router.delete("/{book_id}", dependencies=[Depends(verify_api_key)])
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")

    db.delete(book)
    db.commit()

    return {"message": f"Book '{book.title}' deleted successfully"}


# ─── Helper ───────────────────────────────────────────────────────────────────
def format_book(book: Book) -> dict:
    return {
        "id": book.id,
        "bookId": book.bookId,
        "title": book.title,
        "author": book.author,
        "year_of_publication": book.year_of_publication,
        "publisher": book.publisher,
        "imageURL_S": book.imageURL_S,
        "imageURL_M": book.imageURL_M,
        "imageURL_L": book.imageURL_L,
        "genres": [{"id": g.id, "name": g.name} for g in book.genres],
        "review_count": len(book.reviews),
    }