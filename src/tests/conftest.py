"""
Pytest configuration and fixtures for testing the Pedigree Tracker application.
"""
import os
import tempfile
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, Session

from app import create_app
from app.database import Base, get_db
from app.models import AnimalType, Animal, Gender

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

# Global engine for the test database
_engine = None

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for testing."""
    app = create_app({
        'TESTING': True,
        'DATABASE_URL': TEST_DATABASE_URL,
        'WTF_CSRF_ENABLED': False,
    })
    
    # Initialize the database
    with app.app_context():
        global _engine
        _engine = create_engine(TEST_DATABASE_URL)
        # Create tables without adding default data
        Base.metadata.create_all(_engine)
    
    yield app
    
    # Clean up
    if _engine:
        _engine.dispose()

@pytest.fixture(scope='session')
def engine(app):
    """Get the database engine for testing."""
    global _engine
    if _engine is None:
        _engine = create_engine(TEST_DATABASE_URL)
    return _engine

@pytest.fixture(scope='function')
def db_session(engine):
    """Create a new database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()
    
    # Create a clean session with the same connection that the app will use
    from app.database import SessionLocal
    # Create a new session factory
    session_factory = sessionmaker(bind=connection, expire_on_commit=False)
    session = scoped_session(session_factory)
    
    # Store original session and replace with test session
    import app.database
    original_session = app.database.SessionLocal
    app.database.SessionLocal = session
    
    # Clear any existing data to ensure a clean test environment
    from sqlalchemy import text
    session.execute(text('PRAGMA foreign_keys = OFF'))
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.execute(text('PRAGMA foreign_keys = ON'))
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Add some test data
    from app.models import AnimalType, Animal, Gender
    from datetime import datetime, timedelta, UTC
    
    # Add test animal types
    cattle = AnimalType(name='Cattle', description='Bovine animals')
    sheep = AnimalType(name='Sheep', description='Ovine animals')
    session.add_all([cattle, sheep])
    
    # Add test animals
    now = datetime.now(UTC)
    animals = [
        Animal(
            identifier='COW001',
            name='Bessie',
            gender=Gender.FEMALE,
            date_of_birth=now - timedelta(days=1000),
            animal_type=cattle,
            is_active=True
        ),
        Animal(
            identifier='SHEEP001',
            name='Dolly',
            gender=Gender.FEMALE,
            date_of_birth=now - timedelta(days=500),
            animal_type=sheep,
            is_active=True
        )
    ]
    session.add_all(animals)
    session.commit()
    
    yield session
    
    # Cleanup
    session.close()
    
    # Only rollback if the transaction is still active
    if transaction.is_active:
        transaction.rollback()
    
    connection.close()
    
    # Restore original SessionLocal
    app.database.SessionLocal = original_session

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def auth_client(client):
    """A test client with authentication headers."""
    # TODO: Implement authentication
    return client

@pytest.fixture
def sample_animal_type(db_session):
    """Create a sample animal type for testing."""
    # Create a unique name for this test
    name = f"TestType_{datetime.now().timestamp()}"
    animal_type = AnimalType(
        name=name,
        description='A test animal type'
    )
    db_session.add(animal_type)
    db_session.commit()
    return animal_type

@pytest.fixture
def sample_animal(db_session, sample_animal_type):
    """Create a sample animal for testing."""
    # Create a unique identifier for this test
    identifier = f"TEST_{datetime.now().timestamp()}"
    animal = Animal(
        identifier=identifier,
        name='Test Animal',
        gender=Gender.FEMALE,
        date_of_birth=datetime.now() - timedelta(days=365),
        animal_type=sample_animal_type,
        is_active=True
    )
    db_session.add(animal)
    db_session.commit()
    return animal
