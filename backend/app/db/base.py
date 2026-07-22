"""
Declarative base for all SQLAlchemy ORM models.

Every model (e.g. LogEvent) must inherit from `Base` so that:
  1. SQLAlchemy tracks them as part of the same metadata.
  2. Alembic's autogenerate can detect schema changes correctly.

Models themselves live under app/models/ — this file only defines the
shared base class they inherit from.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class that all ORM models will inherit from."""

    pass
