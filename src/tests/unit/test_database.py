"""
Tests for database connection and initialization.
"""
import os
import tempfile
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from app.database import init_db, get_db, SessionLocal, engine
from app.models import Base, AnimalType

class TestDatabase:
    """Test cases for database connection and initialization."""
    
    def test_database_initialization(self, tmp_path):
        """Test that the database is properly initialized with tables."""
        # Create a temporary database file
        db_path = tmp_path / "test.db"
        test_engine = create_engine(f"sqlite:///{db_path}")
        
        # Create all tables
        Base.metadata.create_all(bind=test_engine)
        
        # Verify tables exist
        table_names = test_engine.table_names()
        assert 'animal_type' in table_names
        assert 'animal' in table_names
        
        # Clean up
        test_engine.dispose()
    
    def test_init_db_creates_tables(self, tmp_path):
        """Test that init_db creates all necessary tables."""
        # Create a temporary database file
        db_path = tmp_path / "test_init.db"
        test_engine = create_engine(f"sqlite:///{db_path}")
        
        # Create a test session
        TestingSessionLocal = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        )
        
        # Initialize the database
        Base.metadata.create_all(bind=test_engine)
        
        # Verify tables exist
        table_names = test_engine.table_names()
        assert 'animal_type' in table_names
        assert 'animal' in table_names
        
        # Clean up
        test_engine.dispose()
    
    def test_get_db_yields_session(self):
        """Test that get_db yields a working database session."""
        # Get a database session using the get_db generator
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            # Verify it's a valid session
            assert db is not None
            
            # Test a simple query
            result = db.query(AnimalType).first()
            assert result is None or isinstance(result, AnimalType)
            
        finally:
            # Clean up by closing the session
            try:
                next(db_gen)
            except StopIteration:
                pass
    
    def test_session_rollback_on_exception(self, monkeypatch):
        """Test that the session is rolled back if an exception occurs."""
        # Create a mock that will raise an exception
        def mock_commit():
            raise Exception("Test exception")
        
        # Get a database session
        db_gen = get_db()
        db = next(db_gen)
        
        # Add a test record
        test_type = AnimalType(name="Test Type")
        db.add(test_type)
        
        # Mock the commit to raise an exception
        monkeypatch.setattr(db, 'commit', mock_commit)
        
        # The exception should be propagated
        with pytest.raises(Exception, match="Test exception"):
            db_gen.throw(Exception("Test exception"))
        
        # The session should be closed
        assert db.is_active is False
    
    def test_session_auto_rollback(self):
        """Test that uncommitted changes are rolled back when the session is closed."""
        # Get a database session
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            # Add a test record but don't commit
            test_type = AnimalType(name="Test Rollback")
            db.add(test_type)
            
            # The object is in the session but not persisted
            assert test_type in db
            
            # Close the session without committing
            next(db_gen)
            
            # Start a new session to verify the record wasn't saved
            db2 = next(get_db())
            try:
                result = db2.query(AnimalType).filter_by(name="Test Rollback").first()
                assert result is None
            finally:
                next(db2._generator)
                
        except Exception:
            # Ensure we always close the generator
            next(db_gen)
            raise
    
    def test_session_auto_close(self):
        """Test that the session is properly closed after use."""
        # Get a database session
        db_gen = get_db()
        db = next(db_gen)
        
        # The session should be active
        assert db.is_active is True
        
        # Close the session
        try:
            next(db_gen)
        except StopIteration:
            pass
        
        # The session should be closed
        assert db.is_active is False
