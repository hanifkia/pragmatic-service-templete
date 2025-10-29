"""
PostgreSQL Database Models Module

This module defines SQLAlchemy ORM models for PostgreSQL database tables.
These are infrastructure models, NOT domain models.

Responsibilities:
    - Define database table schemas
    - Handle ORM relationships
    - Manage database constraints

Key Difference:
    - UserModel = Database representation (has ORM magic)
    - User = Domain representation (pure Python, no DB knowledge)

Example:
    >>> # This is a database model (infrastructure)
    >>> class UserModel(Base):
    ...     __tablename__ = "users"
    ...     id = Column(UUID, primary_key=True)
    ...     email = Column(String, unique=True)
    >>>
    >>> # This is converted to/from domain User model
"""

import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class UserModel(Base):
    """
    SQLAlchemy model for users table in PostgreSQL.

    This is the database representation of a user.
    The repository layer converts between this and the domain User model.

    Table Schema:
        users:
            - id: UUID primary key
            - email: unique string
            - hashed_password: string
            - full_name: string
            - is_active: boolean (default True)
            - is_superuser: boolean (default False)
            - created_at: timestamp (auto-set)
            - updated_at: timestamp (auto-updated)

    Example:
        >>> # SQLAlchemy usage (in repository only!)
        >>> db_user = UserModel(
        ...     email="john@example.com",
        ...     hashed_password="$2b$12$...",
        ...     full_name="John Doe"
        ... )
        >>> session.add(db_user)
        >>> await session.commit()
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self):
        return f"<UserModel(id={self.id}, email={self.email})>"
