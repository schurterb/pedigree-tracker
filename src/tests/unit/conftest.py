"""
Pytest configuration and fixtures for unit tests.
"""
import os
import tempfile
import pytest
from datetime import datetime, UTC

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from app.models import Base, AnimalType, Animal, Gender

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope='session')
def engine():
    """Create a database engine for testing."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
    return engine

@pytest.fixture(scope='function')
def db_session(engine):
    """Create a new database session for a test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session
    connection = engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(bind=connection)
    Session = scoped_session(session_factory)
    session = Session()
    
    # Add test data
    try:
        # Add default animal types
        cattle = AnimalType(name='Cattle', description='Bovine animals')
        sheep = AnimalType(name='Sheep', description='Ovine animals')
        session.add_all([cattle, sheep])
        
        # Add some test animals
        now = datetime.now(UTC)
        animals = [
            Animal(
                identifier='COW001',
                name='Bessie',
                gender=Gender.FEMALE,
                date_of_birth=now.replace(year=now.year - 2),
                animal_type=cattle,
                is_active=True
            ),
            Animal(
                identifier='SHEEP001',
                name='Dolly',
                gender=Gender.FEMALE,
                date_of_birth=now.replace(year=now.year - 1),
                animal_type=sheep,
                is_active=True
            )
        ]
        session.add_all(animals)
        
        # Add animals with parents
        animals_with_parents = [
            Animal(
                identifier='COW002',
                name='Daisy',
                gender=Gender.FEMALE,
                date_of_birth=now.replace(year=now.year - 1, month=6),
                animal_type=cattle,
                mother=animals[0],  # Bessie is the mother
                is_active=True
            ),
            Animal(
                identifier='SHEEP002',
                name='Shaun',
                gender=Gender.MALE,
                date_of_birth=now.replace(year=now.year - 1, month=7),
                animal_type=sheep,
                mother=animals[1],  # Dolly is the mother
                is_active=True
            )
        ]
        session.add_all(animals_with_parents)
        
        session.commit()
        
        # Store references to the created objects
        session.cattle = cattle
        session.sheep = sheep
        session.bessie = animals[0]
        session.dolly = animals[1]
        session.daisy = animals_with_parents[0]
        session.shaun = animals_with_parents[1]
        
        yield session
        
    finally:
        # Clean up the session
        session.close()
        
        # Only rollback if the transaction is still active
        if transaction.is_active:
            transaction.rollback()
            
        connection.close()

@pytest.fixture
def sample_animal_type(db_session):
    """Create a sample animal type for testing."""
    animal_type = AnimalType(name='Test Type', description='Test Description')
    db_session.add(animal_type)
    db_session.commit()
    return animal_type

@pytest.fixture
def sample_animal(db_session, sample_animal_type):
    """Create a sample animal for testing."""
    animal = Animal(
        identifier='TEST001',
        name='Test Animal',
        gender=Gender.MALE,
        date_of_birth=datetime.utcnow().date(),
        animal_type=sample_animal_type,
        is_active=True
    )
    db_session.add(animal)
    db_session.commit()
    return animal
