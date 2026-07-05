"""
Database engine and session management.

Provides:
  - `engine`: the SQLAlchemy engine connected to PostgreSQL.
  - `SessionLocal`: a session factory for creating DB sessions.
  - `get_db`: a FastAPI dependency that yields a session per request
    and guarantees it is closed afterwards.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # verifies connections are alive before using them
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session per request.

    Usage in an endpoint:
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
