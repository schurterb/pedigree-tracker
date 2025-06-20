"""
Database connection and session management.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError

from .config import DATABASE_URI
from .models import Base

# Create database engine
engine = create_engine(
    DATABASE_URI,
    echo=False,  # Set to True for SQL query logging
    connect_args={"check_same_thread": False}  # SQLite specific
)

# Create a configured "Session" class
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

def init_db(create_default_data=False):  # Default changed to False - no default data by default
    """Initialize the database by creating all tables.
    
    Args:
        create_default_data (bool): If True, creates default animal types if none exist.
    """
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(DATABASE_URI.replace('sqlite:///', '')), exist_ok=True)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Check environment variable to override default data creation
    if os.environ.get('PEDIGREE_CREATE_DEFAULT_DATA') == '1':
        create_default_data = True
    
    if create_default_data:
        from .models import AnimalType
        
        session = SessionLocal()
        try:
            print("Creating default animal types...")
            # Check if we already have any animal types
            if session.query(AnimalType).count() == 0:  # Changed to count() for more reliable check
                # Add some default animal types
                default_types = [
                    AnimalType(name='Cattle', description='Bovine animals'),
                    AnimalType(name='Sheep', description='Ovine animals'),
                    AnimalType(name='Goats', description='Caprine animals'),
                    AnimalType(name='Horses', description='Equine animals'),
                    AnimalType(name='Pigs', description='Porcine animals'),
                    AnimalType(name='Chickens', description='Poultry birds'),
                ]
                
                for animal_type in default_types:
                    session.add(animal_type)
                    
                session.commit()
                print("Added default animal types to the database.")
        except Exception as e:
            session.rollback()
            print(f"Error initializing database with default data: {e}")
        finally:
            session.close()

def get_db():
    """
    Dependency function to get a database session.
    
    Yields:
        Session: A SQLAlchemy database session.
    """
    db = SessionLocal()
    db._generator = iter([None])  # Provide a proper generator for test functions
    try:
        yield db
        db.commit()  # Auto-commit successful transactions
    except SQLAlchemyError as e:
        db.rollback()
        raise e  # Re-raise the exception after rollback
    except Exception:
        # For any other exception, ensure rollback
        db.rollback()
        raise
    finally:
        db.close()  # Always close the session

# Initialize the database when this module is imported
init_db(create_default_data=False)
