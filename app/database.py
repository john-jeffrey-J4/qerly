from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from config import get_settings
from sqlalchemy.pool import QueuePool
from fastapi import Request, HTTPException
from fastapi import FastAPI

SQLALCHEMY_DATABASE_URL = get_settings().database_url

POOL_SIZE = 10
MAX_OVERFLOW = -1
POOL_TIMEOUT = 30

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=QueuePool,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db(request: Request):
    if not hasattr(request.state, "database_url") or not request.state.database_url:
        raise HTTPException(status_code=404, detail="The database information is not available.")

    database_url = request.state.database_url
    print("current db detail: ",database_url)
    engine = create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=POOL_SIZE,
        max_overflow=MAX_OVERFLOW,
        pool_timeout=POOL_TIMEOUT
    )
    SessionLocal.configure(bind=engine)
    
    with SessionLocal() as db:  # Use context manager to ensure session cleanup
        try:
            yield db
        finally:
            db.close()

