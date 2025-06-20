"""
Test cases for the Animal Type API endpoints.
"""
import pytest
from datetime import datetime, timezone, UTC
from app.models.animal_type import AnimalType
from sqlalchemy.exc import IntegrityError
from .conftest import API_TEST_PREFIX

# Use API_TEST_PREFIX from conftest.py
def test_api_route_diagnostics(client, api_url_debug):
    """Diagnostic test to verify API routes and URL handling."""
    # Get a response from the API root to check connectivity
    response = client.get(API_TEST_PREFIX, follow_redirects=True)
    print(f"\nDEBUG - API Root Response: {response.status_code}")
    
    # Print URL we're trying to access
    animal_types_url = f'{API_TEST_PREFIX}/animal-types/'
    print(f"\nDEBUG - Animal Types URL: {animal_types_url}")
    
    # Make a test request
    response = client.get(animal_types_url, follow_redirects=True)
    print(f"DEBUG - Response Status: {response.status_code}")
    print(f"DEBUG - Response Data: {response.data}\n")
    
    # No assertions - this is just for diagnostic purposes

def test_get_animal_types(client, db_session, app):
    """Test retrieving all animal types."""
    # Make the request - don't include leading slash as test client handles it
    url = f'{API_TEST_PREFIX}/animal-types/'
    response = client.get(url, follow_redirects=True)
    
    # Debug output
    print(f"DEBUG: Response status code: {response.status_code}")
    print(f"DEBUG: Response data: {response.data}")
    
    # Verify the response structure and status code
    assert response.status_code == 200
    assert isinstance(response.json, list)
    
    # Verify that we got some animal types
    assert len(response.json) > 0, "No animal types returned in response"
    
    # Verify the structure of each animal type in the response
    required_fields = {'id', 'name', 'description', 'created_at', 'updated_at'}
    for animal_type in response.json:
        # Check that all required fields are present
        assert all(field in animal_type for field in required_fields), \
            f"Missing required fields in animal type: {animal_type}"
        
        # Check that the ID is an integer
        assert isinstance(animal_type['id'], int), "ID should be an integer"
        
        # Check that the name is a non-empty string
        assert isinstance(animal_type['name'], str), "Name should be a string"
        assert len(animal_type['name']) > 0, "Name should not be empty"
        
        # Check that the description is a string (can be None or empty)
        assert animal_type['description'] is None or isinstance(animal_type['description'], str), \
            "Description should be a string or null"

def test_get_single_animal_type(client, db_session):
    """Test retrieving a single animal type by ID."""
    # Find an existing animal type (created in the db_session fixture)
    animal_type = db_session.query(AnimalType).filter_by(name='Cattle').first()
    assert animal_type is not None, "Test data 'Cattle' not found in database"
    
    # Test retrieving the animal type
    response = client.get(f'{API_TEST_PREFIX}/animal-types/{animal_type.id}')
    assert response.status_code == 200
    data = response.json
    assert data['id'] == animal_type.id
    assert data['name'] == 'Cattle'

def test_create_animal_type(client, db_session):
    """Test creating a new animal type."""
    # Clear any existing data
    db_session.query(AnimalType).delete()
    db_session.commit()
    
    # Create a unique name for the test
    unique_name = f'TestType_{datetime.now(UTC).timestamp()}'
    data = {
        'name': unique_name,
        'description': 'Test description'
    }
    response = client.post(f'{API_TEST_PREFIX}/animal-types/', json=data)
    assert response.status_code == 201
    assert response.json['name'] == unique_name
    assert 'id' in response.json
    
    # Verify it was saved to the database
    saved_type = db_session.query(AnimalType).filter_by(name=unique_name).first()
    assert saved_type is not None
    assert saved_type.description == 'Test description'
    
    # Test creating a duplicate (should fail with 409)
    response = client.post(f'{API_TEST_PREFIX}/animal-types/', json=data)
    assert response.status_code == 409

def test_update_animal_type(client, db_session):
    """Test updating an existing animal type."""
    # Clear any existing data
    db_session.query(AnimalType).delete()
    db_session.commit()
    
    # First create a type to update
    test_type = AnimalType(name='TestType', description='Original description')
    db_session.add(test_type)
    db_session.commit()
    
    update_data = {
        'name': 'UpdatedType',
        'description': 'Updated description'
    }
    response = client.put(
        f'{API_TEST_PREFIX}/animal-types/{test_type.id}',
        json=update_data
    )
    assert response.status_code == 200
    assert response.json['name'] == 'UpdatedType'
    assert response.json['description'] == 'Updated description'
    
    # Verify the update in the database
    updated = db_session.get(AnimalType, test_type.id)
    assert updated.name == 'UpdatedType'
    assert updated.description == 'Updated description'

def test_delete_animal_type(client, db_session):
    """Test deleting an animal type."""
    # Clear any existing data
    # First delete animals to avoid foreign key constraint violations
    from app.models.animal import Animal
    db_session.query(Animal).delete()
    db_session.query(AnimalType).delete()
    db_session.commit()
    
    # First create a type to delete with a unique name
    unique_name = f'ToDelete_{datetime.now(UTC).timestamp()}'
    test_type = AnimalType(name=unique_name, description='Will be deleted')
    db_session.add(test_type)
    db_session.commit()
    type_id = test_type.id
    
    # Verify it exists
    response = client.get(f'{API_TEST_PREFIX}/animal-types/{type_id}')
    assert response.status_code == 200
    
    # Now delete it
    response = client.delete(f'{API_TEST_PREFIX}/animal-types/{type_id}')
    assert response.status_code == 204
    
    # Verify it's gone
    response = client.get(f'{API_TEST_PREFIX}/animal-types/{type_id}')
    assert response.status_code == 404
    
    # Verify it's removed from the database
    deleted = db_session.get(AnimalType, type_id)
    assert deleted is None
