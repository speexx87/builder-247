from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, UTC

Base = declarative_base()

class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(UTC))
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(UTC))
    conversation = relationship("Conversation", back_populates="messages")

class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    level = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(UTC))

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
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC))

    def __repr__(self):
        return f"<Transaction(id={self.id}, status='{self.status}', created_at='{self.created_at}')>"