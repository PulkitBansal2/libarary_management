from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware
from app.database import engine
from app import models
from app.routers import users, books
from fastapi.templating import Jinja2Templates

# Create all tables if they don't exist.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Library Management System")

# Add session middleware with a secret key (change in production)
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# Mount routers
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(books.router, prefix="/books", tags=["books"])

# Home endpoint that renders the base template
@app.get("/")
def read_root(request: Request):
    templates = Jinja2Templates(directory="templates")
    return templates.TemplateResponse("base.html", {"request": request})
