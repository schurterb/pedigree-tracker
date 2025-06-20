"""
Tests for the Animal model.
"""
import pytest
from datetime import datetime, date

from app.models import Animal, AnimalType, Gender
from tests.unit.test_base import TestBase

class TestAnimal(TestBase):
    """Test cases for the Animal model."""
    
    def test_animal_creation(self):
        """Test creating a new animal with required fields."""
        # Create a new animal
        new_animal = Animal(
            identifier='COW999',
            name='Milky',
            gender=Gender.FEMALE,
            animal_type=self.cattle,
            is_active=True
        )
        
        self.db.add(new_animal)
        self.db.commit()
        
        # Verify the animal was created correctly
        assert new_animal.id is not None
        assert new_animal.identifier == 'COW999'
        assert new_animal.name == 'Milky'
        assert new_animal.gender == Gender.FEMALE
        assert new_animal.animal_type == self.cattle
        assert new_animal.is_active is True
        assert isinstance(new_animal.created_at, datetime)
        assert isinstance(new_animal.updated_at, datetime)
    
    def test_animal_required_fields(self):
        """Test that required fields are enforced."""
        # Missing identifier
        with pytest.raises(Exception):
            animal = Animal(
                name='No Identifier',
                gender=Gender.MALE,
                animal_type=self.cattle
            )
            self.db.add(animal)
            self.db.commit()
        self.db.rollback()
        
        # Missing animal_type
        with pytest.raises(Exception):
            animal = Animal(
                identifier='NO_TYPE',
                name='No Type',
                gender=Gender.MALE
            )
            self.db.add(animal)
            self.db.commit()
        self.db.rollback()
    
    def test_animal_identifier_uniqueness(self):
        """Test that animal identifiers must be unique."""
        # Try to create a duplicate identifier
        with pytest.raises(Exception):
            duplicate = Animal(
                identifier='COW001',  # Duplicate of animal1
                name='Duplicate',
                gender=Gender.MALE,
                animal_type=self.cattle
            )
            self.db.add(duplicate)
            self.db.commit()
        self.db.rollback()
    
    def test_animal_parent_relationships(self):
        """Test parent-child relationships between animals."""
        # Create a new animal with parents
        child = Animal(
            identifier='COW003',
            name='Junior',
            gender=Gender.MALE,
            animal_type=self.cattle,
            mother=self.animal1,
            father=self.animal3  # animal3 is also a child of animal1
        )
        
        self.db.add(child)
        self.db.commit()
        
        # Verify relationships
        assert child.mother == self.animal1
        assert child.father == self.animal3
        
        # Verify backrefs
        assert child in self.animal1.offspring
        assert child in self.animal3.offspring
        
        # Verify the offspring count
        assert len(self.animal1.offspring) == 2  # animal3 and child
        assert len(self.animal3.offspring) == 1  # just child
    
    def test_animal_string_representation(self):
        """Test the string representation of Animal."""
        assert str(self.animal1) == '<Animal COW001>'
    
    def test_animal_soft_delete(self):
        """Test soft delete functionality."""
        # Initially should be active
        assert self.animal1.is_active is True
        
        # Soft delete
        self.animal1.is_active = False
        self.db.commit()
        
        # Should be marked as inactive
        assert self.animal1.is_active is False
        
        # Should still exist in the database
        animal = self.db.get(Animal, self.animal1.id)
        assert animal is not None
        assert animal.is_active is False
    
    def test_animal_date_validation(self):
        """Test date validation for date_of_birth."""
        # Future date should be allowed but might trigger a warning in a real app
        future_animal = Animal(
            identifier='FUTURE001',
            name='Future Cow',
            gender=Gender.FEMALE,
            animal_type=self.cattle,
            date_of_birth=date(2099, 1, 1)
        )
        self.db.add(future_animal)
        self.db.commit()
        
        # Verify the date was stored correctly
        assert future_animal.date_of_birth == date(2099, 1, 1)
    
    def test_animal_gender_validation(self):
        """Test that only valid gender values are allowed."""
        # Valid gender
        valid_animal = Animal(
            identifier='VALID001',
            name='Valid Gender',
            gender=Gender.MALE,
            animal_type=self.cattle
        )
        self.db.add(valid_animal)
        self.db.commit()
        
        # Invalid gender should raise an error
        with pytest.raises(ValueError):
            invalid_animal = Animal(
                identifier='INVALID001',
                name='Invalid Gender',
                gender='INVALID',
                animal_type=self.cattle
            )
            # Need to access the enum to trigger validation
            _ = invalid_animal.gender
        
        self.db.rollback()
    
    def test_animal_type_relationship(self):
        """Test the relationship between Animal and AnimalType."""
        # Verify the relationship is set up correctly
        assert self.animal1.animal_type == self.cattle
        assert self.animal2.animal_type == self.sheep
        
        # Verify the backref works
        assert self.animal1 in self.cattle.animals
        assert self.animal2 in self.sheep.animals
