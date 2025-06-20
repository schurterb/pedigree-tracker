"""
Fixtures for API tests.
"""
import pytest
from datetime import datetime, timedelta
from flask import url_for
from app.config import API_PREFIX

# Ensure API_PREFIX is correctly formatted for tests
API_TEST_PREFIX = API_PREFIX.rstrip('/')

@pytest.fixture
def auth_headers():
    """Return authentication headers for API requests."""
    return {
        'Authorization': 'Bearer test-token',
        'Content-Type': 'application/json'
    }

@pytest.fixture
def sample_animal_data(sample_animal_type):
    """Return sample animal data for testing."""
    return {
        'identifier': 'TEST001',
        'name': 'Test Animal',
        'gender': 'female',
        'date_of_birth': (datetime.utcnow() - timedelta(days=365)).strftime('%Y-%m-%d'),
        'description': 'A test animal',
        'type_id': sample_animal_type.id,
        'is_active': True
    }

@pytest.fixture
def sample_animal_type_data():
    """Return sample animal type data for testing."""
    return {
        'name': 'Test Type',
        'description': 'A test animal type'
    }

@pytest.fixture
def api_url_debug(app):
    """Print and return diagnostic information about API routes."""
    with app.test_request_context():
        # Get all registered routes in the app
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'path': rule.rule
            })
        
        print(f"\nDEBUG - Registered Routes:")
        for route in routes:
            print(f"  {route['path']} - {route['methods']} - {route['endpoint']}")
        
        # Debug specifically for animal-types routes
        animal_type_routes = [r for r in routes if 'animal-types' in r['path']]
        print(f"\nDEBUG - Animal Type Routes:")
        for route in animal_type_routes:
            print(f"  {route['path']} - {route['methods']} - {route['endpoint']}")
        
        # Debug specifically for animals routes
        animal_routes = [r for r in routes if 'animals' in r['path'] and 'animal-types' not in r['path']]
        print(f"\nDEBUG - Animal Routes:")
        for route in animal_routes:
            print(f"  {route['path']} - {route['methods']} - {route['endpoint']}")
            
    return routes
