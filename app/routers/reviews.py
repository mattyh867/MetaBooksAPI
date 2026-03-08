from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.models import Review, Book, User
from app.auth import verify_api_key


router = APIRouter()


# ─── GET /reviews ─────────────────────────────────────────────────────────────
# List all reviews, optionally filtered by book or user
@router.get("/")
def get_reviews(
    book_id: Optional[int] = Query(None, description="Filter by book ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    min_rating: Optional[int] = Query(None, ge=1, le=10, description="Minimum rating"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(Review)

    if book_id:
        query = query.filter(Review.book_id == book_id)
    if user_id:
        query = query.filter(Review.user_id == user_id)
    if min_rating:
        query = query.filter(Review.rating >= min_rating)

    total = query.count()
    reviews = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": [format_review(r) for r in reviews]
    }


# ─── GET /reviews/{id} ────────────────────────────────────────────────────────
# Get a single review by ID
@router.get("/{review_id}")
def get_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        raise HTTPException(status_code=404, detail=f"Review with id {review_id} not found")

    return format_review(review)


# ─── POST /reviews ────────────────────────────────────────────────────────────
# Create a new review for a book
@router.post("/", status_code=201, dependencies=[Depends(verify_api_key)])
def create_review(payload: dict, db: Session = Depends(get_db)):
    # Validate book exists
    book = db.query(Book).filter(Book.id == payload.get("book_id")).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with id {payload.get('book_id')} not found")

    # Validate user exists
    user = db.query(User).filter(User.id == payload.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {payload.get('user_id')} not found")

    # Prevent duplicate review from same user on same book
    existing = db.query(Review).filter(
        Review.book_id == payload.get("book_id"),
        Review.user_id == payload.get("user_id")
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="User has already reviewed this book")

    review = Review(**payload)
    db.add(review)
    db.commit()
    db.refresh(review)

    return {"message": "Review created successfully", "review": format_review(review)}


# ─── PUT /reviews/{id} ────────────────────────────────────────────────────────
# Update a review
@router.put("/{review_id}", dependencies=[Depends(verify_api_key)])
def update_review(review_id: int, payload: dict, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        raise HTTPException(status_code=404, detail=f"Review with id {review_id} not found")

    for field, value in payload.items():
        if hasattr(review, field):
            setattr(review, field, value)

    db.commit()
    db.refresh(review)

    return {"message": "Review updated successfully", "review": format_review(review)}


# ─── DELETE /reviews/{id} ─────────────────────────────────────────────────────
# Delete a review
@router.delete("/{review_id}", dependencies=[Depends(verify_api_key)])
def delete_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        raise HTTPException(status_code=404, detail=f"Review with id {review_id} not found")

    db.delete(review)
    db.commit()

    return {"message": f"Review {review_id} deleted successfully"}


# ─── Helper ───────────────────────────────────────────────────────────────────
def format_review(review: Review) -> dict:
    return {
        "id": review.id,
        "book_id": review.book_id,
        "user_id": review.user_id,
        "content": review.content,
        "rating": review.rating,
        "book_title": review.book.title if review.book else None,
        "reviewer": review.user.username if review.user else None,
    }