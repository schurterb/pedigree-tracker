"""
Test cases for the Animal API endpoints.
"""
import pytest
from datetime import date, datetime, timedelta, timezone, UTC

from app.models.animal import Animal, Gender
from app.models.animal_type import AnimalType
from sqlalchemy.exc import IntegrityError
from .conftest import API_TEST_PREFIX

def test_get_animals(client, db_session):
    """Test retrieving all animals."""
    # Clear any existing data
    db_session.query(Animal).delete()
    db_session.query(AnimalType).delete()
    db_session.commit()
    
    # Add a test animal type and animal
    animal_type = AnimalType(name='TestType', description='Test type')
    db_session.add(animal_type)
    
    animal = Animal(
        identifier='TEST001',
        name='Test Animal',
        gender=Gender.FEMALE,
        date_of_birth=datetime.now(UTC).date(),
        animal_type=animal_type,
        is_active=True
    )
    db_session.add(animal)
    db_session.commit()
    
    response = client.get(f'{API_TEST_PREFIX}/animals/', follow_redirects=True)
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0
    assert any(a['identifier'] == 'TEST001' for a in response.json)

def test_get_single_animal(client, db_session):
    """Test retrieving a single animal by ID."""
    # Clear any existing data
    db_session.query(Animal).delete()
    db_session.query(AnimalType).delete()
    db_session.commit()
    
    # Add a test animal type and animal
    animal_type = AnimalType(name='TestType', description='Test type')
    db_session.add(animal_type)
    
    animal = Animal(
        identifier='TEST001',
        name='Test Animal',
        gender=Gender.FEMALE,
        date_of_birth=datetime.now(UTC).date(),
        animal_type=animal_type,
        is_active=True
    )
    db_session.add(animal)
    db_session.commit()
    
    response = client.get(f'{API_TEST_PREFIX}/animals/{animal.id}')
    assert response.status_code == 200
    data = response.json
    assert data['id'] == animal.id
    assert data['identifier'] == 'TEST001'
    assert data['name'] == 'Test Animal'

def test_create_animal(client, db_session):
    """Test creating a new animal."""
    # Clear any existing data
    db_session.query(Animal).delete()
    db_session.query(AnimalType).delete()
    db_session.commit()
    
    # First create an animal type
    animal_type = AnimalType(name='TestType', description='Test type')
    db_session.add(animal_type)
    db_session.commit()
    
    data = {
        'identifier': 'NEW001',
        'name': 'New Animal',
        'gender': 'male',
        'date_of_birth': '2022-01-01',
        'type_id': animal_type.id,
        'is_active': True
    }
    response = client.post(f'{API_TEST_PREFIX}/animals/', json=data)
    print(f"\nDEBUG - Response status: {response.status_code}")
    print(f"DEBUG - Response data: {response.data}")
    assert response.status_code == 201
    assert response.json['identifier'] == 'NEW001'
    assert 'id' in response.json
    
    # Verify it was saved to the database
    saved_animal = db_session.query(Animal).filter_by(identifier='NEW001').first()
    assert saved_animal is not None
    assert saved_animal.name == 'New Animal'
    assert saved_animal.gender == 'male'

def test_update_animal(client, db_session):
    """Test updating an existing animal."""
    # Clear any existing data
    db_session.query(Animal).delete()
    db_session.query(AnimalType).delete()
    db_session.commit()
    
    # First create an animal type and animal
    animal_type = AnimalType(name='TestType', description='Test type')
    db_session.add(animal_type)
    
    animal = Animal(
        identifier='TEST001',
        name='Original Name',
        gender=Gender.FEMALE,
        date_of_birth=datetime.now(UTC).date(),
        animal_type=animal_type,
        is_active=True
    )
    db_session.add(animal)
    db_session.commit()
    
    update_data = {
        'name': 'Updated Name',
        'description': 'Updated description',
        'type_id': animal_type.id,
        'identifier': 'TEST001',
        'gender': 'female',
        'is_active': True
    }
    
    response = client.put(
        f'{API_TEST_PREFIX}/animals/{animal.id}',
        json=update_data
    )
    assert response.status_code == 200
    assert response.json['name'] == 'Updated Name'
    assert response.json['description'] == 'Updated description'
    
    # Verify the update in the database
    updated = db_session.get(Animal, animal.id)
    assert updated.name == 'Updated Name'
    assert updated.description == 'Updated description'

def test_delete_animal(client, db_session):
    """Test deleting an animal."""
    # Clear any existing data
    db_session.query(Animal).delete()
    db_session.query(AnimalType).delete()
    db_session.commit()
    
    # First create an animal type and animal
    animal_type = AnimalType(name='TestType', description='Test type')
    db_session.add(animal_type)
    
    animal = Animal(
        identifier='TODELETE',
        name='To Be Deleted',
        gender=Gender.FEMALE,
        date_of_birth=datetime.now(UTC).date(),
        animal_type=animal_type,
        is_active=True
    )
    db_session.add(animal)
    db_session.commit()
    animal_id = animal.id
    
    # Verify it exists
    response = client.get(f'{API_TEST_PREFIX}/animals/{animal_id}')
    assert response.status_code == 200
    
    # Now delete it
    response = client.delete(f'{API_TEST_PREFIX}/animals/{animal_id}')
    assert response.status_code == 204
    
    # Verify it's gone
    response = client.get(f'{API_TEST_PREFIX}/animals/{animal_id}')
    assert response.status_code == 404
    
    # Verify it's removed from the database
    deleted = db_session.get(Animal, animal_id)
    assert deleted is None

def test_animal_pedigree(client, db_session):
    """Test retrieving an animal's pedigree."""
    # Clear any existing data
    db_session.query(Animal).delete()
    db_session.query(AnimalType).delete()
    db_session.commit()
    
    # Create animal type
    animal_type = AnimalType(name='TestType', description='Test type')
    db_session.add(animal_type)
    db_session.commit()
    
    # Create grandpa
    grandpa = Animal(
        identifier='GP001',
        name='Grandpa',
        gender=Gender.MALE,
        date_of_birth=date(2010, 1, 1),
        animal_type=animal_type,
        is_active=True
    )
    db_session.add(grandpa)
    
    # Create grandma
    grandma = Animal(
        identifier='GM001',
        name='Grandma',
        gender=Gender.FEMALE,
        date_of_birth=date(2010, 2, 1),
        animal_type=animal_type,
        is_active=True
    )
    db_session.add(grandma)
    
    # Create father
    father = Animal(
        identifier='F001',
        name='Father',
        gender=Gender.MALE,
        date_of_birth=date(2015, 1, 1),
        father=grandpa,
        mother=grandma,
        animal_type=animal_type,
        is_active=True
    )
    db_session.add(father)
    
    # Create mother
    mother = Animal(
        identifier='M001',
        name='Mother',
        gender=Gender.FEMALE,
        date_of_birth=date(2015, 2, 1),
        animal_type=animal_type,
        is_active=True
    )
    db_session.add(mother)
    
    # Create child
    child = Animal(
        identifier='C001',
        name='Child',
        gender=Gender.MALE,
        date_of_birth=date(2020, 1, 1),
        father=father,
        mother=mother,
        animal_type=animal_type,
        is_active=True
    )
    db_session.add(child)
    db_session.commit()
    
    # Get the pedigree
    response = client.get(f'{API_TEST_PREFIX}/animals/{child.id}/pedigree')
    assert response.status_code == 200
    pedigree = response.json
    
    # Verify the pedigree structure
    assert pedigree['name'] == 'Child'
    assert pedigree['father']['name'] == 'Father'
    assert pedigree['mother']['name'] == 'Mother'
    assert pedigree['father']['father']['name'] == 'Grandpa'
    assert pedigree['father']['mother']['name'] == 'Grandma'
