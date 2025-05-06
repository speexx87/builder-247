import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prometheus_swarm.database.models import Base, Transaction
from prometheus_swarm.database.transaction_cleanup import cleanup_expired_transactions

@pytest.fixture(scope="function")
def test_engine():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create a session for database interactions"""
    TestSessionLocal = sessionmaker(bind=test_engine)
    session = TestSessionLocal()
    yield session
    session.close()

def test_cleanup_expired_transactions(test_session):
    """Test cleaning up expired transactions"""
    # Create test transactions
    current_time = datetime.utcnow()
    
    # Add an expired incomplete transaction
    expired_transaction = Transaction(
        status='pending',
        created_at=current_time - timedelta(hours=25)
    )
    
    # Add a recent incomplete transaction
    recent_transaction = Transaction(
        status='pending',
        created_at=current_time - timedelta(hours=1)
    )
    
    # Add a completed transaction
    completed_transaction = Transaction(
        status='completed',
        created_at=current_time - timedelta(hours=25)
    )
    
    test_session.add_all([expired_transaction, recent_transaction, completed_transaction])
    test_session.commit()

    # Monkey patch SessionLocal to return our test session
    from prometheus_swarm.database.transaction_cleanup import SessionLocal
    original_sessionlocal = SessionLocal
    SessionLocal = lambda: test_session

    try:
        # Call cleanup function
        deleted_count = cleanup_expired_transactions(expiration_hours=24)

        # Verify results
        assert deleted_count == 1, f"Expected 1 transaction to be deleted, got {deleted_count}"

        # Check remaining transactions
        remaining_transactions = test_session.query(Transaction).all()
        assert len(remaining_transactions) == 2
        assert all(t.status in ['pending', 'completed'] for t in remaining_transactions)

    finally:
        # Restore original SessionLocal
        SessionLocal = original_sessionlocal

def test_cleanup_no_expired_transactions(test_session):
    """Test cleaning up when no transactions are expired"""
    current_time = datetime.utcnow()
    
    # Add recent transactions
    recent_transactions = [
        Transaction(status='pending', created_at=current_time - timedelta(hours=1)),
        Transaction(status='pending', created_at=current_time - timedelta(hours=2))
    ]
    
    test_session.add_all(recent_transactions)
    test_session.commit()

    # Monkey patch SessionLocal to return our test session
    from prometheus_swarm.database.transaction_cleanup import SessionLocal
    original_sessionlocal = SessionLocal
    SessionLocal = lambda: test_session

    try:
        # Call cleanup function
        deleted_count = cleanup_expired_transactions(expiration_hours=24)

        # Verify no transactions were deleted
        assert deleted_count == 0, f"Expected 0 transactions to be deleted, got {deleted_count}"
        assert test_session.query(Transaction).count() == 2

    finally:
        # Restore original SessionLocal
        SessionLocal = original_sessionlocal

def test_cleanup_with_custom_expiration(test_session):
    """Test cleaning up with a custom expiration time"""
    current_time = datetime.utcnow()
    
    # Create test transactions
    expired_transaction = Transaction(
        status='pending',
        created_at=current_time - timedelta(hours=3)
    )
    
    recent_transaction = Transaction(
        status='pending',
        created_at=current_time - timedelta(hours=1)
    )
    
    test_session.add_all([expired_transaction, recent_transaction])
    test_session.commit()

    # Monkey patch SessionLocal to return our test session
    from prometheus_swarm.database.transaction_cleanup import SessionLocal
    original_sessionlocal = SessionLocal
    SessionLocal = lambda: test_session

    try:
        # Call cleanup function with 2-hour expiration
        deleted_count = cleanup_expired_transactions(expiration_hours=2)

        # Verify results
        assert deleted_count == 1, f"Expected 1 transaction to be deleted, got {deleted_count}"
        
        # Ensure only the expired transaction was deleted
        remaining_transactions = test_session.query(Transaction).all()
        assert len(remaining_transactions) == 1
        assert remaining_transactions[0].status == 'pending'
        assert remaining_transactions[0].created_at > current_time - timedelta(hours=2)

    finally:
        # Restore original SessionLocal
        SessionLocal = original_sessionlocal