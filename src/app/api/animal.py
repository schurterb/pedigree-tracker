"""
Animal API resource for managing animals and their genealogical data.
"""
import logging

from flask import request
from flask_restx import Namespace, Resource, fields
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from ..models import Animal, AnimalType, Gender
from ..database import get_session
from .validation import (
    ValidationError,
    get_json_object,
    parse_animal_payload,
    validate_lineage,
)

logger = logging.getLogger(__name__)

# Create namespace
ns = Namespace("animals", description="Animal operations")

# Request/response models
animal_model = ns.model(
    "Animal",
    {
        "id": fields.Integer(readOnly=True, description="The animal unique identifier"),
        "identifier": fields.String(
            required=True,
            description="Unique identifier within the animal type (e.g., tag number)",
        ),
        "name": fields.String(description="Name of the animal"),
        "gender": fields.String(
            enum=Gender.values(), description="Gender of the animal"
        ),
        "date_of_birth": fields.Date(
            description="Date of birth (YYYY-MM-DD, not in the future)"
        ),
        "description": fields.String(description="Description of the animal"),
        "notes": fields.String(description="Additional notes"),
        "is_active": fields.Boolean(description="Whether the animal is active"),
        "type_id": fields.Integer(required=True, description="Animal type ID"),
        "animal_type": fields.Nested(
            ns.model("AnimalTypeRef", {"id": fields.Integer, "name": fields.String}),
            attribute="animal_type",
        ),
        "mother_id": fields.Integer(
            description="Mother animal ID (must be female and of the same type)"
        ),
        "father_id": fields.Integer(
            description="Father animal ID (must be male and of the same type)"
        ),
        "created_at": fields.DateTime(readOnly=True, description="Creation timestamp"),
        "updated_at": fields.DateTime(
            readOnly=True, description="Last update timestamp"
        ),
    },
)

# For creating/updating animals (excludes read-only fields).
# Defined explicitly - an inherit() with None values breaks schema generation.
animal_input_model = ns.model(
    "AnimalInput",
    {
        "identifier": fields.String(
            required=True,
            description="Unique identifier within the animal type (e.g., tag number)",
        ),
        "name": fields.String(description="Name of the animal"),
        "gender": fields.String(
            enum=Gender.values(), description="Gender of the animal"
        ),
        "date_of_birth": fields.Date(
            description="Date of birth (YYYY-MM-DD, not in the future)"
        ),
        "description": fields.String(description="Description of the animal"),
        "notes": fields.String(description="Additional notes"),
        "is_active": fields.Boolean(description="Whether the animal is active"),
        "type_id": fields.Integer(required=True, description="Animal type ID"),
        "mother_id": fields.Integer(
            description="Mother animal ID (must be female and of the same type)"
        ),
        "father_id": fields.Integer(
            description="Father animal ID (must be male and of the same type)"
        ),
    },
)

validation_error_model = ns.model(
    "ValidationError",
    {
        "message": fields.String(description="Summary of the validation failure"),
        "errors": fields.Raw(description="Mapping of field name to error message"),
    },
)

ANIMAL_FIELDS = (
    "identifier",
    "name",
    "gender",
    "date_of_birth",
    "description",
    "notes",
    "is_active",
)


def _commit(db, identifier, existing_animal=None):
    """Commit the session, translating integrity errors into aborts."""
    try:
        db.commit()
        return True
    except IntegrityError as e:
        db.rollback()
        if "identifier" in str(e.orig).lower() or "uq_animal" in str(e.orig).lower():
            ns.abort(
                409,
                message=(
                    f"Animal with identifier '{identifier}' "
                    "already exists in this category."
                ),
            )
        logger.exception("Unexpected integrity error saving animal")
        ns.abort(400, message="Could not save animal.")


def _get_animal_or_404(db, id):
    animal = db.get(Animal, id)
    if animal is None:
        ns.abort(404, message=f"Animal with ID {id} not found.")
    return animal


def _apply_update(db, animal, parsed):
    """Apply a validated partial payload to an existing animal."""
    proposed = {
        "type_id": parsed.get("type_id", animal.type_id),
        "gender": parsed.get("gender", animal.gender),
        "date_of_birth": parsed.get("date_of_birth", animal.date_of_birth)
        if "date_of_birth" in parsed
        else animal.date_of_birth,
        "mother_id": parsed.get("mother_id", animal.mother_id)
        if "mother_id" in parsed
        else animal.mother_id,
        "father_id": parsed.get("father_id", animal.father_id)
        if "father_id" in parsed
        else animal.father_id,
    }
    errors = {}
    validate_lineage(db, animal, proposed, errors)
    if "type_id" in parsed:
        if not db.get(AnimalType, parsed["type_id"]):
            errors["type_id"] = f"Invalid animal type ID: {parsed['type_id']}"
    if errors:
        raise ValidationError("Invalid animal data.", errors=errors)

    if "type_id" in parsed:
        animal.animal_type = db.get(AnimalType, parsed["type_id"])
    if "mother_id" in parsed:
        animal.mother_id = parsed["mother_id"]  # explicit null clears
    if "father_id" in parsed:
        animal.father_id = parsed["father_id"]

    for field in ANIMAL_FIELDS:
        if field in parsed:
            try:
                setattr(animal, field, parsed[field])
            except ValueError as e:
                db.rollback()
                raise ValidationError(
                    "Invalid animal data.", errors={field: "Invalid value."}
                ) from e


@ns.route("/")
class AnimalList(Resource):
    """Shows a list of all animals, and lets you POST to add new animals."""

    @ns.doc("list_animals")
    @ns.param("type_id", "Filter by animal type ID")
    @ns.param("active", "Filter by active status (true/false)")
    @ns.param("search", "Search term for name or identifier")
    @ns.marshal_list_with(animal_model)
    def get(self):
        """List all animals with optional filtering."""
        db = get_session()
        query = db.query(Animal).options(joinedload(Animal.animal_type))

        # Apply filters
        if "type_id" in request.args:
            query = query.filter(Animal.type_id == request.args["type_id"])

        if "active" in request.args:
            is_active = request.args["active"].lower() == "true"
            query = query.filter(Animal.is_active == is_active)

        if "search" in request.args:
            search = f"%{request.args['search']}%"
            query = query.filter(
                (Animal.name.ilike(search)) | (Animal.identifier.ilike(search))
            )

        return query.all()

    @ns.doc("create_animal")
    @ns.expect(animal_input_model)
    @ns.marshal_with(animal_model, code=201)
    @ns.response(400, "Validation error", validation_error_model)
    @ns.response(409, "Identifier already exists in this category")
    def post(self):
        """Create a new animal."""
        data = get_json_object()
        db = get_session()
        parsed = parse_animal_payload(data, partial=False)

        errors = {}
        if not db.get(AnimalType, parsed["type_id"]):
            errors["type_id"] = f"Invalid animal type ID: {parsed['type_id']}"
        else:
            validate_lineage(
                db,
                None,
                {
                    "type_id": parsed["type_id"],
                    "gender": parsed.get("gender", Gender.UNKNOWN),
                    "date_of_birth": parsed.get("date_of_birth"),
                    "mother_id": parsed.get("mother_id"),
                    "father_id": parsed.get("father_id"),
                },
                errors,
            )
        if errors:
            raise ValidationError("Invalid animal data.", errors=errors)

        animal_type = db.get(AnimalType, parsed["type_id"])

        # Create animal
        try:
            animal = Animal(
                identifier=parsed["identifier"],
                animal_type=animal_type,
                name=parsed.get("name"),
                gender=parsed.get("gender", Gender.UNKNOWN),
                date_of_birth=parsed.get("date_of_birth"),
                description=parsed.get("description"),
                notes=parsed.get("notes"),
                is_active=parsed.get("is_active", True),
                mother_id=parsed.get("mother_id"),
                father_id=parsed.get("father_id"),
            )
        except ValueError as e:
            db.rollback()
            raise ValidationError(
                "Invalid animal data.", errors={"gender": "Invalid value."}
            ) from e

        db.add(animal)
        _commit(db, parsed["identifier"])
        db.refresh(animal)
        return animal, 201


@ns.route("/<int:id>")
@ns.response(404, "Animal not found")
@ns.param("id", "The animal identifier")
class AnimalResource(Resource):
    """Show a single animal and lets you delete or update it."""

    @ns.doc("get_animal")
    @ns.marshal_with(animal_model)
    def get(self, id):
        """Fetch a single animal by ID with its type information."""
        db = get_session()
        animal = _get_animal_or_404(db, id)
        return animal

    @ns.doc("update_animal")
    @ns.expect(animal_input_model)
    @ns.marshal_with(animal_model)
    @ns.response(400, "Validation error", validation_error_model)
    @ns.response(409, "Identifier already exists in this category")
    def put(self, id):
        """Update an existing animal.

        Fields absent from the body are left unchanged. Setting
        ``mother_id`` or ``father_id`` to ``null`` clears that parent.
        """
        data = get_json_object()
        db = get_session()
        animal = _get_animal_or_404(db, id)
        parsed = parse_animal_payload(data, partial=True)

        _apply_update(db, animal, parsed)

        _commit(db, parsed.get("identifier", animal.identifier))
        db.refresh(animal)
        return animal

    @ns.doc("delete_animal")
    @ns.response(204, "Animal deleted")
    @ns.response(400, "Animal has recorded offspring")
    def delete(self, id):
        """Delete an animal."""
        db = get_session()
        animal = _get_animal_or_404(db, id)

        # Check if this animal is a parent of any other animals
        children = (
            db.query(Animal)
            .filter((Animal.mother_id == id) | (Animal.father_id == id))
            .count()
        )

        if children > 0:
            ns.abort(
                400, message="Cannot delete animal that is a parent of other animals."
            )

        db.delete(animal)
        try:
            db.commit()
            return "", 204
        except Exception:
            db.rollback()
            logger.exception("Failed to delete animal %s", id)
            ns.abort(400, message="Could not delete animal.")


@ns.route("/<int:id>/pedigree")
@ns.response(404, "Animal not found")
@ns.param("id", "The animal identifier")
class AnimalPedigree(Resource):
    """Get the pedigree of an animal."""

    @ns.doc("get_animal_pedigree")
    @ns.param(
        "generations",
        "Number of generations to include (1-5, default: 3; "
        "values above 5 are clamped)",
    )
    def get(self, id):
        """Get the pedigree tree of an animal."""
        try:
            generations = int(request.args.get("generations", 3))
        except (TypeError, ValueError):
            ns.abort(400, message="Generations must be an integer between 1 and 5.")
        if generations < 1:
            ns.abort(400, message="Generations must be an integer between 1 and 5.")
        generations = min(generations, 5)

        db = get_session()

        def get_pedigree(animal_id, current_gen, max_gen):
            """Recursively build pedigree tree."""
            if current_gen > max_gen or animal_id is None:
                return None

            animal = db.get(Animal, animal_id)
            if not animal:
                return None

            return {
                "id": animal.id,
                "identifier": animal.identifier,
                "name": animal.name,
                "gender": animal.gender,
                "date_of_birth": animal.date_of_birth.isoformat()
                if animal.date_of_birth
                else None,
                "animal_type": animal.animal_type.name if animal.animal_type else None,
                "mother": get_pedigree(animal.mother_id, current_gen + 1, max_gen),
                "father": get_pedigree(animal.father_id, current_gen + 1, max_gen),
            }

        # Check if animal exists
        _get_animal_or_404(db, id)

        # Build pedigree tree directly
        return get_pedigree(id, 1, generations)
