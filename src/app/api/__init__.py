"""
API Blueprint for the Pedigree Tracker application.
"""
from flask import Blueprint
from flask_restx import Api

# Create API blueprint
api_bp = Blueprint('api', __name__)

# Initialize Flask-RestX API
api = Api(
    api_bp,
    version='1.0',
    title='Pedigree Tracker API',
    description='REST API for managing animal pedigrees',
    doc='/docs'  # Enable Swagger UI at /api/v1/docs/
)

# Import resources to register routes with the API
from . import animal_type  # noqa
from . import animal  # noqa
from . import animal_offspring  # noqa

# Add namespaces
from .animal_type import ns as animal_type_ns
from .animal import ns as animal_ns

api.add_namespace(animal_type_ns)
api.add_namespace(animal_ns)
