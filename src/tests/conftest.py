"""
Pytest configuration and fixtures for testing the Pedigree Tracker application.
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from app import create_app
from app.database import Base
from app.models import AnimalType, Animal, Gender

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

# Global engine for the test database
_engine = None


@pytest.fixture(scope="session")
def app():
    """Create and configure a new app instance for testing."""
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_URL": TEST_DATABASE_URL,
            "WTF_CSRF_ENABLED": False,
        }
    )

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


@pytest.fixture(scope="session")
def engine(app):
    """Get the database engine for testing."""
    global _engine
    if _engine is None:
        _engine = create_engine(TEST_DATABASE_URL)
    return _engine


@pytest.fixture(scope="function")
def db_session(app, tmp_path, monkeypatch):
    """Create an isolated, real file-backed database per test.

    Each test gets its own SQLite file and session registry, patched into
    ``app.database.SessionLocal`` so request handlers share it. Request
    teardown closes the registry's session per request - this detaches ORM
    objects created by fixtures, so tests should capture primitive ids
    before issuing requests rather than reading lazy attributes afterwards.
    """
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)

    registry = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))
    monkeypatch.setattr("app.database.SessionLocal", registry)
    session = registry()

    # Add some test data
    from app.models import AnimalType, Animal, Gender
    from datetime import datetime, timedelta, UTC

    # Add test animal types
    cattle = AnimalType(name="Cattle", description="Bovine animals")
    sheep = AnimalType(name="Sheep", description="Ovine animals")
    session.add_all([cattle, sheep])

    # Add test animals
    now = datetime.now(UTC)
    animals = [
        Animal(
            identifier="COW001",
            name="Bessie",
            gender=Gender.FEMALE,
            date_of_birth=(now - timedelta(days=1000)).date(),
            animal_type=cattle,
            is_active=True,
        ),
        Animal(
            identifier="SHEEP001",
            name="Dolly",
            gender=Gender.FEMALE,
            date_of_birth=(now - timedelta(days=500)).date(),
            animal_type=sheep,
            is_active=True,
        ),
    ]
    session.add_all(animals)
    session.commit()

    yield session

    # Cleanup
    session.close()
    registry.remove()
    engine.dispose()


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
    animal_type = AnimalType(name=name, description="A test animal type")
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
        name="Test Animal",
        gender=Gender.FEMALE,
        date_of_birth=datetime.now() - timedelta(days=365),
        animal_type=sample_animal_type,
        is_active=True,
    )
    db_session.add(animal)
    db_session.commit()
    return animal
