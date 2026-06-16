import secrets
import string
from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas


def generate_short_code(length: int = 6) -> str:
    characters = string.ascii_letters + string.digits
    return "".join(secrets.choice(characters) for _ in range(length))


def create_url(db: Session, url: schemas.URLCreate) -> models.URL:
    # Keep generating until we get a code that doesn't already exist
    short_code = generate_short_code()
    while get_url_by_short_code(db, short_code):
        short_code = generate_short_code()

    db_url = models.URL(target_url=url.target_url, short_code=short_code)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url


def get_url_by_short_code(db: Session, short_code: str) -> models.URL | None:
    return db.query(models.URL).filter(models.URL.short_code == short_code).first()


def create_click(db: Session, url_id: int, referrer: str | None = None) -> models.Click:
    db_click = models.Click(url_id=url_id, referrer=referrer)
    db.add(db_click)
    db.commit()
    db.refresh(db_click)
    return db_click


def get_click_count(db: Session, url_id: int) -> int:
    return db.query(models.Click).filter(models.Click.url_id == url_id).count()