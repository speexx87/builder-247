import datetime
from sqlalchemy import and_
from .database import SessionLocal
from .models import Transaction

def cleanup_expired_transactions(expiration_hours=24):
    """
    Clean up transactions that have expired beyond a specified time threshold.

    Args:
        expiration_hours (int, optional): Number of hours after which a transaction 
                                          is considered expired. Defaults to 24.

    Returns:
        int: Number of transactions deleted
    """
    try:
        # Create a database session
        session = SessionLocal()

        # Calculate the expiration timestamp
        expiration_time = datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=expiration_hours)

        # Find and delete expired transactions
        expired_transactions = session.query(Transaction).filter(
            and_(
                Transaction.created_at < expiration_time,
                Transaction.status != 'completed'
            )
        )

        # Count the number of transactions to be deleted
        transaction_count = expired_transactions.count()

        # Delete the expired transactions
        expired_transactions.delete(synchronize_session=False)

        # Commit the changes
        session.commit()

        return transaction_count

    except Exception as e:
        # If an error occurs, rollback the session
        session.rollback()
        raise e

    finally:
        # Always close the session
        session.close()