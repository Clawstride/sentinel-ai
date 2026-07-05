"""
Declarative base for all SQLAlchemy ORM models.

Every future model (e.g. User, Case, Alert) must inherit from `Base`
so that:
  1. SQLAlchemy can track them as part of the same metadata.
  2. Alembic's autogenerate can detect schema changes correctly.

This file intentionally does NOT import any models yet, since no
business models exist in this MVP foundation step. When models are
added later (e.g. app/models/user.py), they should import this Base.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class that all ORM models will inherit from."""

    pass
