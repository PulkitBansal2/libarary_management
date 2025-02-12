# from fastapi import APIRouter, Depends, Request, HTTPException, Form
# from sqlalchemy.orm import Session
# from app import schemas, crud
# from app.database import SessionLocal
# from datetime import datetime
# from fastapi.templating import Jinja2Templates

# router = APIRouter()

# templates = Jinja2Templates(directory="templates")

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # # Create new user endpoint

# @router.get("/create")
# def create_user_get(request: Request):
#     """
#     Render the create user form.
#     """
#     return templates.TemplateResponse("create_user.html", {"request": request})

# @router.post("/create")
# def create_user_post(
#     request: Request,
#     username: str = Form(...),
#     password: str = Form(...),
#     db: Session = Depends(get_db)
# ):
#     """
#     Process the create user form data.
#     If user creation is successful, redirect to the login page.
#     If an error occurs, re-render the create user form with an error message.
#     """
#     try:
#         crud.create_user(db=db, user=schemas.UserCreate(username=username, password=password))
#         from fastapi.responses import RedirectResponse
#         return RedirectResponse(url="/users/login", status_code=302)
#     except HTTPException as e:
#         return templates.TemplateResponse("create_user.html", {"request": request, "error": e.detail})




# # Render login page
# @router.get("/login")
# def login_get(request: Request):
#     from fastapi.templating import Jinja2Templates
#     templates = Jinja2Templates(directory="templates")
#     return templates.TemplateResponse("login.html", {"request": request})

# # Login form submission
# @router.post("/login")
# def login_post(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
#     from fastapi.templating import Jinja2Templates
#     templates = Jinja2Templates(directory="templates")
#     try:
#         user = crud.authenticate_user(db=db, username=username, password=password)
#         request.session["user_id"] = user.id
#         request.session["username"] = user.username
#         # On successful login, render profile template
#         return templates.TemplateResponse("profile.html", {
#             "request": request,
#             "username": user.username,
#             "notifications": [],
#             "currently_borrowed_books": []
#         })
#     except HTTPException:
#         # On failed login, render login with error
#         return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})

# # Logout endpoint
# @router.get("/logout")
# def logout(request: Request):
#     request.session.clear()
#     from fastapi.responses import RedirectResponse
#     return RedirectResponse(url="/users/login", status_code=302)

# # User profile endpoint
# @router.get("/profile", response_model=schemas.ProfileOut)
# def profile(request: Request, db: Session = Depends(get_db)):
#     user_id = request.session.get("user_id")
#     if not user_id:
#         raise HTTPException(status_code=401, detail="Not logged in")
#     borrows = crud.get_borrows_for_user(db=db, user_id=user_id)
#     notifications = []
#     currently_borrowed_books = []
#     for borrow in borrows:
#         if borrow.return_date is None:
#             currently_borrowed_books.append({
#                 "id": borrow.book.id,
#                 "title": borrow.book.title,
#                 "author": borrow.book.author,
#                 "available": borrow.book.available
#             })
#             days_borrowed = (datetime.utcnow() - borrow.borrow_date).days
#             if days_borrowed > 7:
#                 overdue_days = days_borrowed - 7
#                 penalty = overdue_days * 50
#                 notifications.append(
#                     f"Book id {borrow.book_id} is overdue by {overdue_days} day(s), incurring a penalty of Rs. {penalty}."
#                 )
#     return {"id": user_id, "username": request.session.get("username"), "notifications": notifications, "currently_borrowed_books": currently_borrowed_books}

# # Borrow book endpoint
# @router.post("/borrow", response_model=schemas.BorrowOut)
# def borrow_book(request: Request, action: schemas.BorrowAction, db: Session = Depends(get_db)):
#     user_id = request.session.get("user_id")
#     if not user_id:
#         raise HTTPException(status_code=401, detail="Not logged in")
#     borrow_data = schemas.BorrowCreate(user_id=user_id, book_id=action.book_id)
#     return crud.borrow_book(db=db, borrow=borrow_data)

# # Return book endpoint
# @router.post("/return", response_model=schemas.BorrowOut)
# def return_book(request: Request, action: schemas.BorrowAction, db: Session = Depends(get_db)):
#     user_id = request.session.get("user_id")
#     if not user_id:
#         raise HTTPException(status_code=401, detail="Not logged in")
#     borrow_data = schemas.BorrowCreate(user_id=user_id, book_id=action.book_id)
#     return crud.return_book(db=db, borrow=borrow_data)

# # Optionally: List all borrows for the user
# @router.get("/borrows", response_model=list[schemas.BorrowOut])
# def get_user_borrows(request: Request, db: Session = Depends(get_db)):
#     user_id = request.session.get("user_id")
#     if not user_id:
#         raise HTTPException(status_code=401, detail="Not logged in")
#     borrows = crud.get_borrows_for_user(db=db, user_id=user_id)
#     updated_borrows = []
#     for borrow in borrows:
#         penalty = borrow.penalty
#         notification = None
#         if borrow.return_date is None:
#             days_borrowed = (datetime.utcnow() - borrow.borrow_date).days
#             if days_borrowed > 7:
#                 overdue_days = days_borrowed - 7
#                 penalty = overdue_days * 50
#                 notification = f"Book is overdue by {overdue_days} day(s) with penalty Rs. {penalty}."
#         updated_borrows.append({
#             "id": borrow.id,
#             "user_id": borrow.user_id,
#             "book_id": borrow.book_id,
#             "borrow_date": borrow.borrow_date,
#             "return_date": borrow.return_date,
#             "penalty": penalty,
#             "notification": notification,
#         })
#     return updated_borrows



from fastapi import APIRouter, Depends, Request, HTTPException, Form
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import SessionLocal
from datetime import datetime
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Create User Endpoints ---

@router.get("/create")
def create_user_get(request: Request):
    """
    Render the create user form.
    """
    return templates.TemplateResponse("create_user.html", {"request": request})

@router.post("/create")
def create_user_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Process the create user form.
    On success, redirect to the login page.
    On failure (e.g. username already exists), re-render the form with an error.
    """
    try:
        crud.create_user(db=db, user=schemas.UserCreate(username=username, password=password))
        return RedirectResponse(url="/users/login", status_code=302)
    except HTTPException as e:
        return templates.TemplateResponse("create_user.html", {"request": request, "error": e.detail})

# --- Login Endpoints ---

@router.get("/login")
def login_get(request: Request):
    """
    Render the login form.
    """
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Process login form submission.
    On success, store session info and redirect to the profile page.
    On failure, re-render the login page with an error message.
    """
    try:
        user = crud.authenticate_user(db=db, username=username, password=password)
        request.session["user_id"] = user.id
        request.session["username"] = user.username
        return RedirectResponse(url="/users/profile", status_code=302)
    except HTTPException:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})

# --- Logout Endpoint ---

@router.get("/logout")
def logout(request: Request):
    """
    Clear the session and redirect to the login page.
    """
    request.session.clear()
    return RedirectResponse(url="/users/login", status_code=302)

# --- Profile Endpoint ---

@router.get("/profile")
def profile(request: Request, db: Session = Depends(get_db)):
    """
    Render the user profile.
    The profile page displays the username, any notifications (e.g., overdue books), 
    and includes forms to borrow or return a book by entering its ID.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not logged in")
    
    borrows = crud.get_borrows_for_user(db=db, user_id=user_id)
    notifications = []
    currently_borrowed_books = []
    for borrow in borrows:
        if borrow.return_date is None:
            currently_borrowed_books.append({
                "id": borrow.book.id,
                "title": borrow.book.title,
                "author": borrow.book.author,
                "available": borrow.book.available
            })
            days_borrowed = (datetime.utcnow() - borrow.borrow_date).days
            if days_borrowed > 7:
                overdue_days = days_borrowed - 7
                penalty = overdue_days * 50
                notifications.append(
                    f"Book id {borrow.book_id} is overdue by {overdue_days} day(s) (Penalty: Rs. {penalty})."
                )
    context = {
        "request": request,
        "username": request.session.get("username"),
        "notifications": notifications,
        "currently_borrowed_books": currently_borrowed_books
    }
    return templates.TemplateResponse("profile.html", context)

# --- Borrow and Return Endpoints (via Forms on Profile) ---

@router.post("/borrow")
def borrow_book(
    request: Request,
    book_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Process borrowing a book.
    The form in the profile page sends a book ID.
    After processing, redirect back to the profile page.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not logged in")
    borrow_data = schemas.BorrowCreate(user_id=user_id, book_id=int(book_id))
    crud.borrow_book(db=db, borrow=borrow_data)
    return RedirectResponse(url="/users/profile", status_code=302)

@router.post("/return")
def return_book(
    request: Request,
    book_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Process returning a book.
    The form in the profile page sends a book ID.
    After processing, redirect back to the profile page.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not logged in")
    borrow_data = schemas.BorrowCreate(user_id=user_id, book_id=int(book_id))
    crud.return_book(db=db, borrow=borrow_data)
    return RedirectResponse(url="/users/profile", status_code=302)
