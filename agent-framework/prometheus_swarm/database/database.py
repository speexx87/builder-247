"""Database service module."""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
from sqlmodel import SQLModel
from contextlib import contextmanager
from typing import Optional, Dict, Any
from .models import Conversation, Message, Log, Base
import json

# Import engine from shared config
from .config import engine

# Create session factory
Session = sessionmaker(bind=engine)
SessionLocal = Session  # Alias for compatibility

def get_db():
    """Get database session."""
    return Session()

def initialize_database():
    """Initialize database tables."""
    Base.metadata.create_all(engine)

@contextmanager
def get_session():
    """Context manager for database sessions."""
    session = get_db()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# Rest of the methods remain the same...