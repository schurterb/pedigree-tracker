"""
Base test class for database tests.
"""
import os
import tempfile
import pytest
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from app.models import Base, AnimalType, Animal, Gender

class TestBase:
    """Base class for database tests with setup and teardown."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self, request):
        """
        Set up test database and session before each test method.
        """
        # Create a temporary SQLite database in memory
        self.engine = create_engine('sqlite:///:memory:')
        self.SessionLocal = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        )
        
        # Create all tables
        Base.metadata.create_all(bind=self.engine)
        
        # Create a test session
        self.db = self.SessionLocal()
        
        # Add test data
        self.setup_test_data()
        
        # Add finalizer to clean up after test
        def teardown():
            self.db.close()
            self.SessionLocal.remove()
            Base.metadata.drop_all(bind=self.engine)
        
        request.addfinalizer(teardown)
    
    def setup_test_data(self):
        """
        Set up test data in the database.
        Override this method in test classes to set up specific test data.
        """
        # Add default animal types
        self.cattle = AnimalType(name='Cattle', description='Bovine animals')
        self.sheep = AnimalType(name='Sheep', description='Ovine animals')
        self.db.add_all([self.cattle, self.sheep])
        self.db.commit()
        
        # Add some test animals
        self.animal1 = Animal(
            identifier='COW001',
            name='Bessie',
            gender=Gender.FEMALE,
            date_of_birth=datetime(2020, 1, 1),
            animal_type=self.cattle,
            is_active=True
        )
        
        self.animal2 = Animal(
            identifier='SHEEP001',
            name='Dolly',
            gender=Gender.FEMALE,
            date_of_birth=datetime(2021, 5, 15),
            animal_type=self.sheep,
            is_active=True
        )
        
        self.db.add_all([self.animal1, self.animal2])
        self.db.commit()
        
        # Add animals with parent relationships
        self.animal3 = Animal(
            identifier='COW002',
            name='Daisy',
            gender=Gender.FEMALE,
            date_of_birth=datetime(2022, 3, 10),
            animal_type=self.cattle,
            mother=self.animal1,
            is_active=True
        )
        
        self.animal4 = Animal(
            identifier='SHEEP002',
            name='Shaun',
            gender=Gender.MALE,
            date_of_birth=datetime(2022, 4, 20),
            animal_type=self.sheep,
            mother=self.animal2,
            is_active=True
        )
        
        self.db.add_all([self.animal3, self.animal4])
        self.db.commit()
        
        # Refresh objects to ensure we have the latest data
        self.db.refresh(self.animal1)
        self.db.refresh(self.animal2)
        self.db.refresh(self.animal3)
        self.db.refresh(self.animal4)
