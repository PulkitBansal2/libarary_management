from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.database import SessionLocal
from fastapi.templating import Jinja2Templates

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

templates = Jinja2Templates(directory="templates")

# Display Books management page
@router.get("/")
def list_books(request: Request, db: Session = Depends(get_db)):
    books = db.query(models.Book).all()
    return templates.TemplateResponse("books.html", {"request": request, "books": books})

# Search books endpoint (by book ID or all books)
@router.get("/search")
def search_books(request: Request, book_id: str = "", db: Session = Depends(get_db)):
    if book_id:
        books = db.query(models.Book).filter(models.Book.id == int(book_id)).all()
    else:
        books = db.query(models.Book).all()
    return templates.TemplateResponse("books.html", {"request": request, "books": books})

# Create new book endpoint
@router.post("/create")
def create_book(request: Request, title: str = Form(...), author: str = Form(...), db: Session = Depends(get_db)):
    crud.create_book(db=db, book=schemas.BookCreate(title=title, author=author))
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/books/", status_code=302)

# # Update book endpoints
# @router.get("/update/{book_id}")
# def update_book_get(request: Request, book_id: int, db: Session = Depends(get_db)):
#     book = crud.get_book(db=db, book_id=book_id)
#     # Render update form (for simplicity, reusing books.html with an extra flag)
#     return templates.TemplateResponse("books.html", {"request": request, "book": book, "update": True})
@router.get("/update/{book_id}")
def update_book_get(request: Request, book_id: int, db: Session = Depends(get_db)):
    book = crud.get_book(db=db, book_id=book_id)
    return templates.TemplateResponse("update_book.html", {"request": request, "book": book})



@router.post("/update/{book_id}")
def update_book_post(request: Request, book_id: int, title: str = Form(...), author: str = Form(...), db: Session = Depends(get_db)):
    crud.update_book(db=db, book_id=book_id, book_update=schemas.BookUpdate(title=title, author=author))
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/books/", status_code=302)

# Delete book endpoint
@router.get("/delete/{book_id}")
def delete_book(request: Request, book_id: int, db: Session = Depends(get_db)):
    crud.delete_book(db=db, book_id=book_id)
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/books/", status_code=302)
