"""
Tests for the database models.
"""
import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models import AnimalType, Animal, Gender


def test_animal_type_creation(sample_animal_type):
    """Test creating an animal type."""
    assert sample_animal_type.id is not None
    assert sample_animal_type.name is not None
    assert sample_animal_type.description is not None
    assert sample_animal_type.created_at is not None
    assert sample_animal_type.updated_at is not None
    assert str(sample_animal_type) == f"<AnimalType {sample_animal_type.name}>"


def test_animal_creation(sample_animal, sample_animal_type):
    """Test creating an animal."""
    assert sample_animal.id is not None
    assert sample_animal.identifier is not None
    assert sample_animal.name == "Test Animal"
    assert sample_animal.gender == Gender.FEMALE
    assert sample_animal.type_id == sample_animal_type.id
    assert sample_animal.is_active is True
    assert sample_animal.created_at is not None
    assert sample_animal.updated_at is not None
    assert str(sample_animal) == f"<Animal {sample_animal.identifier}>"


def test_animal_parent_relationships(db_session, sample_animal_type):
    """Test parent-child relationships between animals."""
    # Create parent animals
    mother = Animal(
        identifier="MOTHER001",
        name="Mother",
        gender=Gender.FEMALE,
        animal_type=sample_animal_type,
    )

    father = Animal(
        identifier="FATHER001",
        name="Father",
        gender=Gender.MALE,
        animal_type=sample_animal_type,
    )

    # Create child animal
    child = Animal(
        identifier="CHILD001",
        name="Child",
        gender=Gender.FEMALE,
        animal_type=sample_animal_type,
        mother=mother,
        father=father,
    )

    db_session.add_all([mother, father, child])
    db_session.commit()

    # Test relationships
    assert child.mother_id == mother.id
    assert child.father_id == father.id
    assert child.mother == mother
    assert child.father == father

    # Test backrefs
    assert child in mother.offspring
    assert child in father.offspring


def test_animal_type_animals_relationship(db_session, sample_animal_type):
    """Test the relationship between AnimalType and Animal."""
    # Create some animals
    animals = [
        Animal(
            identifier=f"ANIMAL{i:03d}",
            name=f"Animal {i}",
            gender=Gender.MALE if i % 2 == 0 else Gender.FEMALE,
            animal_type=sample_animal_type,
        )
        for i in range(5)
    ]

    db_session.add_all(animals)
    db_session.commit()

    # Test the relationship
    for animal in animals:
        assert animal in sample_animal_type.animals
        assert animal.animal_type == sample_animal_type


def test_animal_soft_delete(db_session, sample_animal):
    """Test soft delete functionality."""
    # Initially should be active
    assert sample_animal.is_active is True

    # Soft delete
    sample_animal.is_active = False
    db_session.commit()

    # Should be marked as inactive
    assert sample_animal.is_active is False

    # Should still exist in the database
    animal = db_session.get(Animal, sample_animal.id)
    assert animal is not None
    assert animal.is_active is False


def test_animal_type_uniqueness(db_session):
    """Test that animal type names must be unique."""
    unique_name = f"Unique Type {datetime.now().timestamp()}"
    # Create first animal type
    animal_type1 = AnimalType(name=unique_name, description="First")
    db_session.add(animal_type1)
    db_session.commit()

    # Try to create another with the same name
    animal_type2 = AnimalType(name=unique_name, description="Second")
    db_session.add(animal_type2)

    # Should raise an integrity error
    with pytest.raises(IntegrityError):
        db_session.commit()

    # Rollback for clean state
    db_session.rollback()


def test_animal_identifier_uniqueness(db_session, sample_animal_type):
    """Identifier must be unique within the same animal type."""
    # Create first animal
    animal1 = Animal(
        identifier="UNIQUE001",
        name="Animal 1",
        gender=Gender.FEMALE,
        animal_type=sample_animal_type,
    )
    db_session.add(animal1)
    db_session.commit()

    # Try to create another with the same identifier in the same type
    animal2 = Animal(
        identifier="UNIQUE001",
        name="Animal 2",
        gender=Gender.MALE,
        animal_type=sample_animal_type,
    )
    db_session.add(animal2)

    # Should raise an integrity error
    with pytest.raises(IntegrityError):
        db_session.commit()

    # Rollback for clean state
    db_session.rollback()


def test_animal_identifier_unique_per_type(db_session, sample_animal_type):
    """The same identifier may be reused in a different animal type."""
    animal1 = Animal(
        identifier="SHARED001",
        name="Animal 1",
        gender=Gender.FEMALE,
        animal_type=sample_animal_type,
    )
    other_type = AnimalType(
        name=f"Other Type {datetime.now().timestamp()}", description="Second type"
    )
    animal2 = Animal(
        identifier="SHARED001",
        name="Animal 2",
        gender=Gender.MALE,
        animal_type=other_type,
    )
    db_session.add_all([animal1, other_type, animal2])
    db_session.commit()

    assert animal1.identifier == animal2.identifier
    assert animal1.type_id != animal2.type_id
