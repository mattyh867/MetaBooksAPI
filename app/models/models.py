from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# ─── Book ─────────────────────────────────────────────────────────────────────
class Book(Base):
    __tablename__ = "book"

    id = Column(Integer, primary_key=True, index=True)
    bookID = Column(String(100), index=True)
    title = Column(String(500), index=True, nullable=False)
    authors = Column(String(300), index=True)
    average_rating = Column(Float, nullable=True)
    isbn = Column(String(20), nullable=True)
    isbn13 = Column(String(20), nullable=True)
    language_code = Column(String(20), nullable=True)
    num_pages = Column(Integer, nullable=True)
    ratings_count = Column(Integer, nullable=True)
    text_reviews_count = Column(Integer, nullable=True)
    publication_date = Column(String(50), nullable=True)
    publisher = Column(String(200), nullable=True, index=True)

    reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Book id={self.id} title='{self.title}'>"


# ─── User ─────────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), index=True, nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    reviews = relationship("Review", back_populates="user")

    def __repr__(self):
        return f"<User id={self.id} username='{self.username}'>"


# ─── Review ───────────────────────────────────────────────────────────────────
class Review(Base):
    __tablename__ = "review"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=True)
    rating = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    book_id = Column(Integer, ForeignKey("book.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)

    book = relationship("Book", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

    def __repr__(self):
        return f"<Review id={self.id} rating={self.rating} book_id={self.book_id}>"