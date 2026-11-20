"""
API Blueprint for the Pedigree Tracker application.
"""
import logging

from flask import Blueprint
from flask_restx import Api

logger = logging.getLogger(__name__)

# Create API blueprint
api_bp = Blueprint("api", __name__)

# Initialize Flask-RestX API
api = Api(
    api_bp,
    version="1.0",
    title="Pedigree Tracker API",
    description="REST API for managing animal pedigrees",
    doc="/docs",  # Swagger UI at /api/v1/docs (both slash forms work)
)

from .validation import ValidationError  # noqa: E402


@api.errorhandler(ValidationError)
def handle_validation_error(error):
    """Translate validation failures into a consistent 400 contract."""
    return {"message": error.message, "errors": error.errors}, 400


# Import resources to register routes with the API
from . import animal_type  # noqa
from . import animal  # noqa
from . import animal_offspring  # noqa

# Add namespaces
from .animal_type import ns as animal_type_ns  # noqa: E402
from .animal import ns as animal_ns  # noqa: E402

api.add_namespace(animal_type_ns)
api.add_namespace(animal_ns)
