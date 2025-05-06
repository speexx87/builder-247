from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

Base = declarative_base()

class Transaction(Base):
    """
    Database model representing a transaction.

    Attributes:
        id (int): Unique identifier for the transaction
        status (str): Current status of the transaction
        created_at (datetime): Timestamp when the transaction was created
    """
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, nullable=False, default='pending')
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Transaction(id={self.id}, status='{self.status}', created_at='{self.created_at}')>"