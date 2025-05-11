# db/base.py
import time

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.config import SQLALCHEMY_DATABASE_URL

def create_engine_with_retry(
    url: str,
    *,
    retries: int = 10,
    delay: int = 3,
    **engine_kwargs
):
    """
    Try to create and test a SQLAlchemy engine, retrying on OperationalError.
    """
    for attempt in range(1, retries + 1):
        try:
            engine = create_engine(url, **engine_kwargs)
            # test the connection immediately
            with engine.connect():
                pass
            print(f"✅ Database connected on attempt {attempt}")
            return engine
        except OperationalError as e:
            print(f"⚠️  DB connect failed (attempt {attempt}/{retries}): {e}")
            if attempt == retries:
                print("❌ All retries exhausted, raising error")
                raise
            time.sleep(delay)

# replace your old create_engine(...) with this:
engine = create_engine_with_retry(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,       # auto-check stale connections
    pool_size=10,             # optional, tune as you like
    max_overflow=20,          # optional
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
