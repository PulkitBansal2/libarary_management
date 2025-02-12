from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# ----- User Schemas -----
class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

# Extended profile schema includes notifications and currently borrowed books.
class ProfileOut(UserOut):
    notifications: Optional[List[str]] = []
    currently_borrowed_books: Optional[List['BookOut']] = []

# ----- Book Schemas -----
class BookCreate(BaseModel):
    title: str
    author: str

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None

    class Config:
        from_attributes = True

class BookOut(BaseModel):
    id: int
    title: str
    author: str
    available: bool

    class Config:
        from_attributes = True

# ----- Borrow Schemas -----
class BorrowCreate(BaseModel):
    user_id: int
    book_id: int

class BorrowOut(BaseModel):
    id: int
    user_id: int
    book_id: int
    borrow_date: datetime
    return_date: Optional[datetime] = None
    penalty: int = 0
    notification: Optional[str] = None

    class Config:
        from_attributes = True

# ----- Borrow Action Schema -----
class BorrowAction(BaseModel):
    book_id: int

# ProfileOut.update_forward_refs()
ProfileOut.model_rebuild()
