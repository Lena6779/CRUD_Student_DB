# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./students.db"  # where the database file is saved

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # needed for SQLite with FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # makes sessions


class Base(DeclarativeBase):  # the parent class for all models
    pass


def get_db():  # gives each request its own session, then closes it for safety
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()