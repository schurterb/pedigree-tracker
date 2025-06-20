"""
Tests for animal model utility methods and properties.
"""
import pytest
import json
from datetime import date, datetime

from app.models import Animal, Gender

def test_animal_age_property(db_session, sample_animal_type):
    """Test the age property of an animal."""
    # Create an animal born 5 years ago
    dob = date.today().replace(year=date.today().year - 5)
    animal = Animal(
        identifier='AGE001',
        name='Test Age',
        gender=Gender.FEMALE,
        animal_type=sample_animal_type,
        date_of_birth=dob
    )
    
    # Test the age property
    assert animal.age == 5
    
    # Test with a future date of birth
    future_dob = date.today().replace(year=date.today().year + 1)
    future_animal = Animal(
        identifier='FUTURE001',
        name='Future Animal',
        gender=Gender.MALE,
        animal_type=sample_animal_type,
        date_of_birth=future_dob
    )
    
    # Age should be 0 for future dates
    assert future_animal.age == 0

def test_animal_is_adult_property(db_session, sample_animal_type):
    """Test the is_adult property of an animal."""
    # Create an adult animal (older than 2 years)
    adult_dob = date.today().replace(year=date.today().year - 3)
    adult = Animal(
        identifier='ADULT001',
        name='Adult Animal',
        gender=Gender.FEMALE,
        animal_type=sample_animal_type,
        date_of_birth=adult_dob
    )
    
    # Create a young animal (less than 2 years)
    young_dob = date.today().replace(year=date.today().year - 1)
    young = Animal(
        identifier='YOUNG001',
        name='Young Animal',
        gender=Gender.MALE,
        animal_type=sample_animal_type,
        date_of_birth=young_dob
    )
    
    # Test the is_adult property
    assert adult.is_adult is True
    assert young.is_adult is False

def test_animal_offspring_count(db_session, sample_animal_type):
    """Test the offspring count for an animal."""
    # Create a parent animal
    parent = Animal(
        identifier='PARENT001',
        name='Parent',
        gender=Gender.FEMALE,
        animal_type=sample_animal_type,
        date_of_birth=date(2010, 1, 1)
    )
    
    # Create some offspring
    offspring = []
    for i in range(3):
        child = Animal(
            identifier=f'CHILD{i:03d}',
            name=f'Child {i}',
            gender=Gender.MALE if i % 2 == 0 else Gender.FEMALE,
            animal_type=sample_animal_type,
            date_of_birth=date(2020 + i, 1, 1),
            mother=parent
        )
        offspring.append(child)
    
    db_session.add_all([parent] + offspring)
    db_session.commit()
    
    # Test the offspring count
    assert len(parent.offspring) == 3
    
    # Test filtering offspring by gender
    male_offspring = [child for child in parent.offspring if child.gender == Gender.MALE]
    female_offspring = [child for child in parent.offspring if child.gender == Gender.FEMALE]
    
    assert len(male_offspring) == 2  # 0 and 2 are male
    assert len(female_offspring) == 1  # 1 is female

def test_animal_pedigree(db_session, sample_animal_type):
    """Test the pedigree retrieval for an animal."""
    # Create a family tree
    # Grandparents
    grandpa = Animal(
        identifier='GRANDPA001',
        name='Grandpa',
        gender=Gender.MALE,
        animal_type=sample_animal_type,
        date_of_birth=date(1990, 1, 1)
    )
    
    grandma = Animal(
        identifier='GRANDMA001',
        name='Grandma',
        gender=Gender.FEMALE,
        animal_type=sample_animal_type,
        date_of_birth=date(1992, 1, 1)
    )
    
    # Parents
    father = Animal(
        identifier='FATHER001',
        name='Father',
        gender=Gender.MALE,
        animal_type=sample_animal_type,
        date_of_birth=date(2010, 1, 1),
        father=grandpa,
        mother=grandma
    )
    
    mother = Animal(
        identifier='MOTHER001',
        name='Mother',
        gender=Gender.FEMALE,
        animal_type=sample_animal_type,
        date_of_birth=date(2011, 1, 1)
    )
    
    # Child
    child = Animal(
        identifier='CHILD001',
        name='Child',
        gender=Gender.MALE,
        animal_type=sample_animal_type,
        date_of_birth=date(2020, 1, 1),
        father=father,
        mother=mother
    )
    
    db_session.add_all([grandpa, grandma, father, mother, child])
    db_session.commit()
    
    # Test the pedigree
    assert child.father == father
    assert child.mother == mother
    assert child.father.father == grandpa
    assert child.father.mother == grandma
    
    # Test the ancestors property
    ancestors = child.ancestors
    assert len(ancestors) == 4  # father, mother, grandpa, grandma
    assert father in ancestors
    assert mother in ancestors
    assert grandpa in ancestors
    assert grandma in ancestors
    
    # Test the descendants property for grandpa
    grandpa_descendants = grandpa.descendants
    assert len(grandpa_descendants) == 2  # father and child
    assert father in grandpa_descendants
    assert child in grandpa_descendants
    assert mother not in grandpa_descendants
    
    # Test the descendants property for mother
    mother_descendants = mother.descendants
    assert len(mother_descendants) == 1  # only child
    assert child in mother_descendants
    assert father not in mother_descendants

def test_animal_to_dict(db_session, sample_animal_type):
    """Test the to_dict method of Animal model."""
    # Create a parent animal
    parent = Animal(
        identifier='PARENT001',
        name='Parent',
        gender=Gender.FEMALE,
        animal_type=sample_animal_type,
        date_of_birth=date(2010, 1, 1),
        is_active=True,
        notes='Test notes',
        external_id='EXT123',
        metadata_json=json.dumps({'key': 'value'}) # Convert to JSON string
    )
    
    # Create a child animal
    child = Animal(
        identifier='CHILD001',
        name='Child',
        gender=Gender.MALE,
        animal_type=sample_animal_type,
        date_of_birth=date(2020, 1, 1),
        mother=parent,
        is_active=True
    )
    
    db_session.add_all([parent, child])
    db_session.commit()
    
    # Test parent's to_dict
    parent_dict = parent.to_dict()
    assert parent_dict['id'] == parent.id
    assert parent_dict['identifier'] == 'PARENT001'
    assert parent_dict['name'] == 'Parent'
    assert parent_dict['gender'] == 'FEMALE'
    assert parent_dict['date_of_birth'] == '2010-01-01'
    assert parent_dict['animal_type_id'] == sample_animal_type.id
    assert parent_dict['is_active'] is True
    assert parent_dict['notes'] == 'Test notes'
    assert parent_dict['external_id'] == 'EXT123'
    assert parent_dict['metadata_json'] == {'key': 'value'}
    assert 'created_at' in parent_dict
    assert 'updated_at' in parent_dict
    assert parent_dict['mother_id'] is None
    assert parent_dict['father_id'] is None
    
    # Test child's to_dict with include_relationships=True
    child_dict = child.to_dict(include_relationships=True)
    assert child_dict['id'] == child.id
    assert child_dict['mother_id'] == parent.id
    assert 'mother' in child_dict
    assert child_dict['mother']['id'] == parent.id
    assert child_dict['mother']['name'] == 'Parent'
    assert 'father' in child_dict
    assert child_dict['father'] is None
    
    # Test with include_relationships=False
    child_dict_simple = child.to_dict(include_relationships=False)
    assert 'mother' not in child_dict_simple
    assert 'father' not in child_dict_simple
    assert child_dict_simple['mother_id'] == parent.id
    
    # Test with custom fields
    custom_dict = child.to_dict(fields=['id', 'name', 'age'])
    assert set(custom_dict.keys()) == {'id', 'name', 'age'}
    assert custom_dict['name'] == 'Child'
    assert isinstance(custom_dict['age'], int)
