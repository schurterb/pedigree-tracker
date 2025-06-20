"""
Tests for the AnimalType model.
"""
import pytest
from datetime import datetime

from app.models import AnimalType, Animal, Gender
from tests.unit.test_base import TestBase

class TestAnimalType(TestBase):
    """Test cases for the AnimalType model."""
    
    def test_animal_type_creation(self):
        """Test creating a new animal type."""
        # Create a new animal type
        dog_type = AnimalType(
            name='Dogs',
            description='Canine animals'
        )
        
        self.db.add(dog_type)
        self.db.commit()
        
        # Verify the animal type was created correctly
        assert dog_type.id is not None
        assert dog_type.name == 'Dogs'
        assert dog_type.description == 'Canine animals'
        assert isinstance(dog_type.created_at, datetime)
        assert isinstance(dog_type.updated_at, datetime)
        assert dog_type.animals == []
    
    def test_animal_type_required_fields(self):
        """Test that name is required for animal type."""
        # Try to create an animal type without a name
        with pytest.raises(Exception):
            animal_type = AnimalType(description='No name')
            self.db.add(animal_type)
            self.db.commit()
        self.db.rollback()
    
    def test_animal_type_name_uniqueness(self):
        """Test that animal type names must be unique."""
        # Try to create a duplicate animal type
        with pytest.raises(Exception):
            duplicate = AnimalType(name='Cattle', description='Duplicate')
            self.db.add(duplicate)
            self.db.commit()
        self.db.rollback()
    
    def test_animal_type_animals_relationship(self):
        """Test the relationship between AnimalType and Animal."""
        # Add a new animal of type cattle
        new_cow = Animal(
            identifier='COW999',
            name='Milky',
            gender=Gender.FEMALE,
            animal_type=self.cattle,
            is_active=True
        )
        self.db.add(new_cow)
        self.db.commit()
        
        # Refresh to get the latest data
        self.db.refresh(self.cattle)
        
        # Count how many animals are assigned to the cattle type
        cattle_animals_count = len(self.cattle.animals)
        
        # Verify the relationship - there should be at least these two animals
        assert new_cow in self.cattle.animals
        assert self.animal1 in self.cattle.animals
        # The test_base also creates animal3 that has self.cattle as type
        assert cattle_animals_count == 3  # animal1, animal3, and new_cow
    
    def test_animal_type_string_representation(self):
        """Test the string representation of AnimalType."""
        assert str(self.cattle) == '<AnimalType Cattle>'
    
    def test_animal_type_update_timestamps(self):
        """Test that updated_at changes when an animal type is updated."""
        original_updated_at = self.cattle.updated_at
        
        # Update the animal type
        self.cattle.description = 'Updated description'
        self.db.commit()
        self.db.refresh(self.cattle)
        
        # Verify the updated_at timestamp changed
        assert self.cattle.updated_at > original_updated_at
    
    def test_animal_type_cascade_delete(self):
        """Test that deleting an animal type with animals raises an error."""
        # Try to delete an animal type that has animals
        with pytest.raises(Exception):
            self.db.delete(self.cattle)
            self.db.commit()
        self.db.rollback()
        
        # Delete the animals first
        for animal in self.cattle.animals:
            self.db.delete(animal)
        self.db.commit()
        
        # Now deletion should work
        self.db.delete(self.cattle)
        self.db.commit()
        
        # Verify deletion
        assert self.db.get(AnimalType, self.cattle.id) is None
