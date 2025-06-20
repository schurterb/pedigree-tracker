"""
Diagnostic tests for the API routes.
"""
import pytest
from flask import url_for
from app.config import API_PREFIX

def test_api_routes(client, app):
    """Test that the API routes are correctly registered."""
    # Get a direct response from the root URL
    with app.test_request_context():
        # Log all registered routes
        print("\nREGISTERED ROUTES:")
        for rule in app.url_map.iter_rules():
            print(f"  - {rule.rule} ({rule.endpoint}) {rule.methods}")
        
        # Try to access a route manually
        try:
            animal_types_url = url_for('api.animal_types_ns_animal_type_list')
            print(f"\nAnimal Types URL: {animal_types_url}")
        except Exception as e:
            print(f"\nError getting URL for animal_types: {e}")
        
        # Try to access the root API endpoint
        try:
            api_url = url_for('api.specs')
            print(f"API docs URL: {api_url}")
        except Exception as e:
            print(f"Error getting URL for API docs: {e}")
    
    # Test direct requests
    print("\nDIRECT REQUEST TESTS:")
    
    # Test root API endpoint
    response = client.get('/api/v1/')
    print(f"  Root API ({'/api/v1/'}): {response.status_code}")
    
    # Test animal types endpoint
    response = client.get('/api/v1/animal-types/')
    print(f"  Animal Types API ({'/api/v1/animal-types/'}): {response.status_code}")
    
    # Test animals endpoint
    response = client.get('/api/v1/animals/')
    print(f"  Animals API ({'/api/v1/animals/'}): {response.status_code}")
    
    # Test API docs endpoint
    response = client.get('/api/v1/docs/')
    print(f"  API Docs ({'/api/v1/docs/'}): {response.status_code}")
    
    # This is a diagnostic test, so there's no need for assertions
    # We're just checking the output to understand the routing issue
    assert True
