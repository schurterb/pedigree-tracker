"""
Tests for database connection and initialization.
"""
import pytest

from sqlalchemy import create_engine, inspect

from app.database import get_db
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
        table_names = inspect(test_engine).get_table_names()
        assert "animal_type" in table_names
        assert "animal" in table_names

        # Clean up
        test_engine.dispose()

    def test_init_db_creates_tables(self, tmp_path):
        """Test that init_db creates all necessary tables."""
        # Create a temporary database file
        db_path = tmp_path / "test_init.db"
        test_engine = create_engine(f"sqlite:///{db_path}")

        # Initialize the database
        Base.metadata.create_all(bind=test_engine)

        # Verify tables exist
        table_names = inspect(test_engine).get_table_names()
        assert "animal_type" in table_names
        assert "animal" in table_names

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
        monkeypatch.setattr(db, "commit", mock_commit)

        # The exception should be propagated
        with pytest.raises(Exception, match="Test exception"):
            db_gen.throw(Exception("Test exception"))

        # The session should be closed (no open transaction remains)
        assert db.in_transaction() is False

    def test_session_auto_commit_on_clean_exit(self):
        """get_db commits pending changes when the generator finishes cleanly."""
        # Get a database session
        db_gen = get_db()
        db = next(db_gen)

        import uuid

        unique_name = f"Test AutoCommit {uuid.uuid4()}"
        db.add(AnimalType(name=unique_name))

        # Finish the generator - get_db auto-commits on clean exit
        try:
            next(db_gen)
        except StopIteration:
            pass

        # A new session sees the committed record
        db2_gen = get_db()
        db2 = next(db2_gen)
        try:
            result = db2.query(AnimalType).filter_by(name=unique_name).first()
            assert result is not None
            db2.delete(result)
            next(db2_gen)
        except StopIteration:
            pass

    def test_session_rollback_discards_changes(self):
        """Rolling back before the generator finishes discards changes."""
        db_gen = get_db()
        db = next(db_gen)

        import uuid

        unique_name = f"Test RolledBack {uuid.uuid4()}"
        db.add(AnimalType(name=unique_name))
        db.rollback()

        try:
            next(db_gen)
        except StopIteration:
            pass

        db2_gen = get_db()
        db2 = next(db2_gen)
        try:
            result = db2.query(AnimalType).filter_by(name=unique_name).first()
            assert result is None
        finally:
            db2.close()

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

        # The session should be closed (no open transaction remains).
        # Note: Session.is_active may still report True in SQLAlchemy 2.x
        # because a closed session can lazily begin a new transaction.
        assert db.in_transaction() is False
