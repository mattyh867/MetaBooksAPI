from pydantic import BaseModel, Field
from typing import Optional


# ─── BOOK SCHEMAS ─────────────────────────────────────────────────────────────

class BookCreate(BaseModel):
    bookID: Optional[str] = Field(None, description="Book ID from dataset", example="0195153448")
    title: str = Field(..., description="Title of the book", example="Classical Mythology")
    authors: str = Field(..., description="Author(s) of the book", example="Mark P. O. Morford")
    average_rating: Optional[float] = Field(None, description="Average rating", example=3.9)
    isbn: Optional[str] = Field(None, description="ISBN-10", example="0195153448")
    isbn13: Optional[str] = Field(None, description="ISBN-13", example="9780195153446")
    language_code: Optional[str] = Field(None, description="Language code", example="eng")
    num_pages: Optional[int] = Field(None, description="Number of pages", example="292")
    ratings_count: Optional[int] = Field(None, description="Total ratings count", example=2)
    text_reviews_count: Optional[int] = Field(None, description="Total text reviews count", example=1)
    publication_date: Optional[str] = Field(None, description="Publication date", example="2002")
    publisher: Optional[str] = Field(None, description="Publisher name", example="Oxford University Press")

    class Config:
        json_schema_extra = {
            "example": {
                "bookID": "0195153448",
                "title": "Classical Mythology",
                "authors": "Mark P. O. Morford",
                "average_rating": 3.9,
                "isbn": "0195153448",
                "isbn13": "9780195153446",
                "language_code": "eng",
                "num_pages": 292,
                "ratings_count": 2,
                "text_reviews_count": 1,
                "publication_date": "2002",
                "publisher": "Oxford University Press"
            }
        }


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, description="New title", example="Classical Mythology")
    authors: Optional[str] = Field(None, description="New author(s)", example="Mark P. O. Morford")
    average_rating: Optional[float] = Field(None, description="Average rating", example=3.9)
    isbn: Optional[str] = Field(None, description="ISBN-10", example="0195153448")
    isbn13: Optional[str] = Field(None, description="ISBN-13", example="9780195153446")
    language_code: Optional[str] = Field(None, description="Language code", example="eng")
    num_pages: Optional[int] = Field(None, description="Number of pages", example=292)
    ratings_count: Optional[int] = Field(None, description="Total ratings count", example=2)
    text_reviews_count: Optional[int] = Field(None, description="Total text reviews count", example=1)
    publication_date: Optional[str] = Field(None, description="Publication date", example="2002")
    publisher: Optional[str] = Field(None, description="Publisher name", example="Oxford University Press")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Classical Mythology (Updated Edition)",
                "publisher": "Oxford University Press"
            }
        }


# ─── REVIEW SCHEMAS ───────────────────────────────────────────────────────────

class ReviewCreate(BaseModel):
    book_id: str = Field(..., description="ID of the book being reviewed (must exist in the database)", example="0195153448")
    user_id: int = Field(..., description="ID of the user submitting the review (must exist in the database)", example=1)
    rating: Optional[float] = Field(None, ge=1.0, le=10.0, description="Rating out of 10 (1.0–10.0)", example=8.5)
    review_text: Optional[str] = Field(None, description="Written review text", example="A comprehensive and well-written introduction to classical mythology.")

    class Config:
        json_schema_extra = {
            "example": {
                "book_id": "0195153448",
                "user_id": 1,
                "rating": 8.5,
                "review_text": "A comprehensive and well-written introduction to classical mythology."
            }
        }


class ReviewUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=1.0, le=10.0, description="Updated rating out of 10", example=9.0)
    review_text: Optional[str] = Field(None, description="Updated review text", example="Even better on a second read — highly recommended.")

    class Config:
        json_schema_extra = {
            "example": {
                "rating": 9.0,
                "review_text": "Even better on a second read — highly recommended."
            }
        }


# ─── USER SCHEMAS ─────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str = Field(..., description="Unique username for the account", example="bookworm99")
    password: str = Field(..., description="Password for the account", example="securepassword123")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "bookworm99",
                "password": "securepassword123"
            }
        }


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, description="New username", example="bookworm2025")
    password: Optional[str] = Field(None, description="New password", example="newpassword456")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "bookworm2025"
            }
        }