"""
Animal Type API resource for managing animal types (categories).
"""
import logging

from flask import request
from flask_restx import Namespace, Resource, fields
from sqlalchemy.exc import IntegrityError

from ..models import AnimalType, Animal, Gender
from ..database import get_session
from .validation import (
    ValidationError,
    get_json_object,
    parse_animal_type_payload,
    check_type_name_available,
)

logger = logging.getLogger(__name__)

# Create namespace
ns = Namespace("animal-types", description="Animal type operations")

# Request/response models
animal_type_model = ns.model(
    "AnimalType",
    {
        "id": fields.Integer(
            readOnly=True, description="The animal type unique identifier"
        ),
        "name": fields.String(required=True, description="The animal type name"),
        "description": fields.String(description="Description of the animal type"),
        "created_at": fields.DateTime(readOnly=True, description="Creation timestamp"),
        "updated_at": fields.DateTime(
            readOnly=True, description="Last update timestamp"
        ),
    },
)

animal_type_input_model = ns.model(
    "AnimalTypeInput",
    {
        "name": fields.String(required=True, description="The animal type name"),
        "description": fields.String(description="Description of the animal type"),
    },
)

validation_error_model = ns.model(
    "AnimalTypeValidationError",
    {
        "message": fields.String(description="Summary of the validation failure"),
        "errors": fields.Raw(description="Mapping of field name to error message"),
    },
)


def _get_type_or_404(db, id):
    animal_type = db.get(AnimalType, id)
    if animal_type is None:
        ns.abort(404, message=f"Animal type with ID {id} not found.")
    return animal_type


@ns.route("/")
class AnimalTypeList(Resource):
    """Shows a list of all animal types, and lets you POST to add new types."""

    @ns.doc("list_animal_types")
    @ns.marshal_list_with(animal_type_model)
    def get(self):
        """List all animal types."""
        db = get_session()
        return db.query(AnimalType).all()

    @ns.doc("create_animal_type")
    @ns.expect(animal_type_input_model)
    @ns.marshal_with(animal_type_model, code=201)
    @ns.response(400, "Validation error", validation_error_model)
    @ns.response(409, "An animal type with this name already exists")
    def post(self):
        """Create a new animal type."""
        data = get_json_object()
        db = get_session()
        parsed = parse_animal_type_payload(data, partial=False)

        if not check_type_name_available(db, parsed["name"]):
            ns.abort(
                409,
                message=(
                    f"Animal type with name '{parsed['name']}' " "already exists."
                ),
            )

        animal_type = AnimalType(
            name=parsed["name"], description=parsed.get("description")
        )

        db.add(animal_type)
        try:
            db.commit()
            db.refresh(animal_type)
            return animal_type, 201
        except IntegrityError:
            db.rollback()
            ns.abort(
                409,
                message=(
                    f"Animal type with name '{parsed['name']}' " "already exists."
                ),
            )


@ns.route("/<int:id>")
@ns.response(404, "Animal type not found")
@ns.param("id", "The animal type identifier")
class AnimalTypeResource(Resource):
    """Show a single animal type and lets you delete or update it."""

    @ns.doc("get_animal_type")
    @ns.marshal_with(animal_type_model)
    def get(self, id):
        """Fetch a single animal type by ID."""
        db = get_session()
        return _get_type_or_404(db, id)

    @ns.doc("update_animal_type")
    @ns.expect(animal_type_input_model)
    @ns.marshal_with(animal_type_model)
    @ns.response(400, "Validation error", validation_error_model)
    @ns.response(409, "An animal type with this name already exists")
    def put(self, id):
        """Update an existing animal type."""
        data = get_json_object()
        db = get_session()
        animal_type = _get_type_or_404(db, id)
        parsed = parse_animal_type_payload(data, partial=True)

        if "name" in parsed:
            if not check_type_name_available(db, parsed["name"], exclude_id=id):
                ns.abort(
                    409,
                    message=(
                        f"Animal type with name '{parsed['name']}' " "already exists."
                    ),
                )
            animal_type.name = parsed["name"]
        if "description" in parsed:
            animal_type.description = parsed["description"]

        try:
            db.commit()
            db.refresh(animal_type)
            return animal_type
        except IntegrityError:
            db.rollback()
            ns.abort(
                409,
                message=(
                    f"Animal type with name '{parsed.get('name')}' " "already exists."
                ),
            )

    @ns.doc("delete_animal_type")
    @ns.response(204, "Animal type deleted")
    @ns.response(400, "Animal type still has animals")
    def delete(self, id):
        """Delete an animal type."""
        db = get_session()
        animal_type = _get_type_or_404(db, id)

        # Check if there are any animals of this type
        if animal_type.animals:
            ns.abort(400, message="Cannot delete a category that still has animals.")

        db.delete(animal_type)
        try:
            db.commit()
            return "", 204
        except Exception:
            db.rollback()
            logger.exception("Failed to delete animal type %s", id)
            ns.abort(400, message="Could not delete animal type.")


@ns.route("/<int:id>/potential-parents")
@ns.response(404, "Animal type not found")
@ns.param("id", "The animal type identifier")
@ns.param("gender", "Filter by gender ('male' or 'female')")
class AnimalTypePotentialParents(Resource):
    """Get potential parents of a specific animal type."""

    @ns.doc("get_potential_parents")
    @ns.response(400, "Validation error", validation_error_model)
    def get(self, id):
        """Get potential parents filtered by animal type and optionally by gender."""
        db = get_session()
        _get_type_or_404(db, id)

        # Get gender filter from query params
        gender = request.args.get("gender")
        if gender is not None and gender not in (Gender.MALE, Gender.FEMALE):
            raise ValidationError(
                "Invalid gender filter.",
                errors={"gender": "gender must be 'male' or 'female'."},
            )

        # Build query
        query = db.query(Animal).filter(Animal.type_id == id)

        # Apply gender filter if provided
        if gender:
            query = query.filter(Animal.gender == gender)

        # Get all matching animals
        animals = query.order_by(Animal.identifier).all()

        # Format response
        return [
            {
                "id": animal.id,
                "identifier": animal.identifier,
                "name": animal.name,
                "gender": animal.gender,
                "type_id": animal.type_id,
            }
            for animal in animals
        ]
