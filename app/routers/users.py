from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.models import User, Review
from app.auth import verify_api_key

router = APIRouter()


# ─── GET /users ───────────────────────────────────────────────────────────────
@router.get("/")
def get_users(
    search: Optional[str] = Query(None, description="Search by username"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(User)

    if search:
        query = query.filter(User.username.ilike(f"%{search}%"))

    total = query.count()
    users = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": [format_user(u) for u in users]
    }


# ─── GET /users/{id} ──────────────────────────────────────────────────────────
@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

    return format_user(user)


# ─── GET /users/{id}/reviews ──────────────────────────────────────────────────
@router.get("/{user_id}/reviews")
def get_user_reviews(
    user_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

    reviews = db.query(Review).filter(Review.user_id == user_id).offset(offset).limit(limit).all()
    total = db.query(Review).filter(Review.user_id == user_id).count()

    return {
        "user_id": user_id,
        "username": user.username,
        "total_reviews": total,
        "reviews": [
            {
                "id": r.id,
                "book_id": r.book_id,
                "book_title": r.book.title if r.book else None,
                "rating": r.rating,
                "content": r.content,
                "created_at": str(r.created_at)
            }
            for r in reviews
        ]
    }


# ─── POST /users ──────────────────────────────────────────────────────────────
@router.post("/", status_code=201)
def create_user(payload: dict, db: Session = Depends(get_db)):
    # Check for duplicate username
    existing = db.query(User).filter(User.username == payload.get("username")).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Username '{payload.get('username')}' is already taken")

    # In a real app you would hash the password here — noted in report
    user = User(
        username=payload.get("username"),
        password=payload.get("password")
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User created successfully", "user": format_user(user)}


# ─── PUT /users/{id} ──────────────────────────────────────────────────────────
@router.put("/{user_id}", dependencies=[Depends(verify_api_key)])
def update_user(user_id: int, payload: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

    # Prevent username being changed to one that already exists
    if "username" in payload:
        existing = db.query(User).filter(
            User.username == payload["username"],
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(status_code=409, detail=f"Username '{payload['username']}' is already taken")

    for field, value in payload.items():
        if hasattr(user, field):
            setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return {"message": "User updated successfully", "user": format_user(user)}


# ─── DELETE /users/{id} ───────────────────────────────────────────────────────
@router.delete("/{user_id}", dependencies=[Depends(verify_api_key)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

    db.delete(user)
    db.commit()

    return {"message": f"User '{user.username}' deleted successfully"}


# ─── Helper ───────────────────────────────────────────────────────────────────
def format_user(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "created_at": str(user.created_at),
        "review_count": len(user.reviews)
    }