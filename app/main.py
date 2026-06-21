from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from . import models, schemas, crud
from .database import engine, SessionLocal

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortener API")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


# Dependency to get a DB session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def serve_homepage(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/shorten", response_model=schemas.URLInfo)
@limiter.limit("5/minute")
def shorten_url(request: Request, url: schemas.URLCreate, db: Session = Depends(get_db)):
    db_url = crud.create_url(db, url)
    total_clicks = crud.get_click_count(db, db_url.id)
    return schemas.URLInfo(
        target_url=db_url.target_url,
        short_code=db_url.short_code,
        created_at=db_url.created_at,
        total_clicks=total_clicks,
    )


@app.get("/{short_code}")
def redirect_to_url(short_code: str, request: Request, db: Session = Depends(get_db)):
    db_url = crud.get_url_by_short_code(db, short_code)
    if db_url is None:
        raise HTTPException(status_code=404, detail="Short URL not found")

    referrer = request.headers.get("referer")
    crud.create_click(db, db_url.id, referrer)

    return RedirectResponse(url=db_url.target_url)


@app.get("/{short_code}/stats", response_model=schemas.URLStats)
def get_url_stats(short_code: str, db: Session = Depends(get_db)):
    db_url = crud.get_url_by_short_code(db, short_code)
    if db_url is None:
        raise HTTPException(status_code=404, detail="Short URL not found")

    total_clicks = crud.get_click_count(db, db_url.id)
    return schemas.URLStats(
        target_url=db_url.target_url,
        short_code=db_url.short_code,
        created_at=db_url.created_at,
        total_clicks=total_clicks,
        clicks=db_url.clicks,
    )