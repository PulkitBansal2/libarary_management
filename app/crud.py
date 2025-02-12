from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from . import models, schemas

# --- User CRUD ---
def create_user(db: Session, user: schemas.UserCreate):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = models.User(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter(models.User.username == username, models.User.password == password).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

# --- Book CRUD ---
def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(title=book.title, author=book.author)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def get_book(db: Session, book_id: int):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

def update_book(db: Session, book_id: int, book_update: schemas.BookUpdate):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    update_data = book_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_book, key, value)
    db.commit()
    db.refresh(db_book)
    return db_book

def delete_book(db: Session, book_id: int):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(db_book)
    db.commit()
    return db_book

# --- Borrow CRUD ---
def borrow_book(db: Session, borrow: schemas.BorrowCreate):
    book = db.query(models.Book).filter(models.Book.id == borrow.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if not book.available:
        raise HTTPException(status_code=400, detail="Book is already borrowed")
    db_borrow = models.Borrow(user_id=borrow.user_id, book_id=borrow.book_id)
    book.available = False
    db.add(db_borrow)
    db.commit()
    db.refresh(db_borrow)
    return db_borrow

def return_book(db: Session, borrow: schemas.BorrowCreate):
    db_borrow = db.query(models.Borrow).filter(
        models.Borrow.user_id == borrow.user_id,
        models.Borrow.book_id == borrow.book_id,
        models.Borrow.return_date.is_(None)
    ).first()
    if not db_borrow:
        raise HTTPException(status_code=400, detail="No active borrow record found")
    now = datetime.utcnow()
    db_borrow.return_date = now
    days_borrowed = (now - db_borrow.borrow_date).days
    penalty = 0
    if days_borrowed > 7:
        overdue_days = days_borrowed - 7
        penalty = overdue_days * 50
    db_borrow.penalty = penalty
    book = db.query(models.Book).filter(models.Book.id == borrow.book_id).first()
    if book:
        book.available = True
    db.commit()
    db.refresh(db_borrow)
    return db_borrow

def get_borrows_for_user(db: Session, user_id: int):
    borrows = db.query(models.Borrow).filter(models.Borrow.user_id == user_id).all()
    return borrows
