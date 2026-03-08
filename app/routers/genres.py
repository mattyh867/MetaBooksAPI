from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.models import Genre, Book
from app.auth import verify_api_key


router = APIRouter()


# ─── GET /genres ──────────────────────────────────────────────────────────────
# List all genres with optional search
@router.get("/")
def get_genres(
    search: Optional[str] = Query(None, description="Search by genre name"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(Genre)

    if search:
        query = query.filter(Genre.name.ilike(f"%{search}%"))

    total = query.count()
    genres = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": [format_genre(g) for g in genres]
    }


# ─── GET /genres/{id} ─────────────────────────────────────────────────────────
# Get a single genre and its books
@router.get("/{genre_id}")
def get_genre(genre_id: int, db: Session = Depends(get_db)):
    genre = db.query(Genre).filter(Genre.id == genre_id).first()

    if not genre:
        raise HTTPException(status_code=404, detail=f"Genre with id {genre_id} not found")

    return {
        **format_genre(genre),
        "books": [
            {"id": b.id, "title": b.title, "author": b.author}
            for b in genre.books[:10]  # preview first 10 books
        ]
    }


# ─── POST /genres ─────────────────────────────────────────────────────────────
# Create a new genre
@router.post("/", status_code=201, dependencies=[Depends(verify_api_key)])
def create_genre(payload: dict, db: Session = Depends(get_db)):
    # Check for duplicate
    existing = db.query(Genre).filter(Genre.name.ilike(payload.get("name", ""))).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Genre '{payload['name']}' already exists")

    genre = Genre(**payload)
    db.add(genre)
    db.commit()
    db.refresh(genre)

    return {"message": "Genre created successfully", "genre": format_genre(genre)}


# ─── PUT /genres/{id} ─────────────────────────────────────────────────────────
# Update a genre
@router.put("/{genre_id}", dependencies=[Depends(verify_api_key)])
def update_genre(genre_id: int, payload: dict, db: Session = Depends(get_db)):
    genre = db.query(Genre).filter(Genre.id == genre_id).first()

    if not genre:
        raise HTTPException(status_code=404, detail=f"Genre with id {genre_id} not found")

    for field, value in payload.items():
        if hasattr(genre, field):
            setattr(genre, field, value)

    db.commit()
    db.refresh(genre)

    return {"message": "Genre updated successfully", "genre": format_genre(genre)}


# ─── DELETE /genres/{id} ──────────────────────────────────────────────────────
# Delete a genre
@router.delete("/{genre_id}", dependencies=[Depends(verify_api_key)])
def delete_genre(genre_id: int, db: Session = Depends(get_db)):
    genre = db.query(Genre).filter(Genre.id == genre_id).first()

    if not genre:
        raise HTTPException(status_code=404, detail=f"Genre with id {genre_id} not found")

    db.delete(genre)
    db.commit()

    return {"message": f"Genre '{genre.name}' deleted successfully"}


# ─── Helper ───────────────────────────────────────────────────────────────────
def format_genre(genre: Genre) -> dict:
    return {
        "id": genre.id,
        "name": genre.name,
        "description": genre.description,
        "book_count": len(genre.books)
    }