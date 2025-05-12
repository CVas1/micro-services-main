import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.config import SQLALCHEMY_DATABASE_URL
from logger import logger  # Import your custom logger

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
            with engine.connect():
                pass
            logger.info(f"✅ Database connected on attempt {attempt}")
            return engine
        except OperationalError as e:
            logger.warning(f"⚠️  DB connect failed (attempt {attempt}/{retries}): {e}")
            if attempt == retries:
                logger.error("❌ All DB retries exhausted, raising error")
                raise
            time.sleep(delay)

# Replace direct engine creation with retry-enabled logic
engine = create_engine_with_retry(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
