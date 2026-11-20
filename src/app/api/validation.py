"""
Request payload and lineage validation helpers for the Animal API.

All business-rule failures raise :class:`ValidationError`, which the API
translates into a 400 response of the form::

    {"message": "...", "errors": {"<field>": "..."}}

No raw SQL or exception details are ever placed in the message.
"""
from datetime import date

from flask import request

from ..models import Animal, AnimalType, Gender


class ValidationError(Exception):
    """Raised when request data fails validation.

    Attributes:
        message: Human-readable summary of the failure.
        errors: Mapping of field name -> field-specific error message.
    """

    def __init__(self, message, errors=None):
        super().__init__(message)
        self.message = message
        self.errors = errors or {}


# Field length limits matching the database columns.
MAX_IDENTIFIER_LEN = 50
MAX_NAME_LEN = 100
MAX_TYPE_NAME_LEN = 50


def get_json_object():
    """Return the request JSON body, enforcing that it is an object.

    Raises:
        ValidationError: if the body is missing, malformed, or not an object.
    """
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        raise ValidationError(
            "Request body must be a JSON object.",
            errors={"body": "Request body must be a JSON object."},
        )
    return data


def _parse_int(value, field, errors, allow_none=True):
    """Coerce value to int (accepting digit strings from HTML selects)."""
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        errors[field] = f"{field} must be an integer."
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.lstrip("-").isdigit():
            return int(stripped)
    errors[field] = f"{field} must be an integer."
    return None


def _parse_dob(value, field, errors):
    """Normalize a date_of_birth value to a date or None."""
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return None
    if isinstance(value, date):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = date.fromisoformat(value.strip())
        except ValueError:
            errors[field] = "Invalid date format. Use YYYY-MM-DD."
            return None
    else:
        errors[field] = "Invalid date format. Use YYYY-MM-DD."
        return None
    if parsed > date.today():
        errors[field] = "Date of birth cannot be in the future."
    return parsed


def _trim_string(value, field, max_len, errors, required=False):
    """Normalize a string field: strip, enforce type/length/blank rules."""
    if value is None:
        if required:
            errors[field] = f"{field.replace('_', ' ').title()} is required."
        return None
    if not isinstance(value, str):
        errors[field] = f"{field} must be a string."
        return None
    value = value.strip()
    if required and not value:
        errors[field] = f"{field.replace('_', ' ').title()} is required."
        return None
    if len(value) > max_len:
        errors[field] = f"{field} must be at most {max_len} characters."
    return value or None


def parse_animal_payload(data, partial=False):
    """Validate and normalize an animal create/update payload.

    Args:
        data: Request JSON dict (already ensured to be a dict).
        partial: When True, only fields present in *data* are validated and
            included in the result (PUT semantics). When False, all fields
            are validated and absent fields get their defaults (POST).

    Returns:
        dict: Normalized values, only for keys that were validated.

    Raises:
        ValidationError: with a mapping of every failing field.
    """
    errors = {}
    out = {}

    def present(field):
        return not partial or field in data

    if present("identifier"):
        value = _trim_string(
            data.get("identifier"),
            "identifier",
            MAX_IDENTIFIER_LEN,
            errors,
            required=True,
        )
        if "identifier" not in errors:
            out["identifier"] = value

    if present("name"):
        out["name"] = _trim_string(data.get("name"), "name", MAX_NAME_LEN, errors)

    if present("gender"):
        gender = data.get("gender", Gender.UNKNOWN if not partial else None)
        if partial and "gender" not in data:
            pass
        elif gender in (None, ""):
            out["gender"] = Gender.UNKNOWN
        elif gender not in Gender.values():
            errors["gender"] = (
                "Invalid gender. Must be one of: " + ", ".join(Gender.values()) + "."
            )
        else:
            out["gender"] = gender

    if present("date_of_birth"):
        if "date_of_birth" not in errors:
            out["date_of_birth"] = _parse_dob(
                data.get("date_of_birth"), "date_of_birth", errors
            )

    if present("description"):
        value = data.get("description")
        if value is not None and not isinstance(value, str):
            errors["description"] = "description must be a string."
        else:
            out["description"] = value

    if present("notes"):
        value = data.get("notes")
        if value is not None and not isinstance(value, str):
            errors["notes"] = "notes must be a string."
        else:
            out["notes"] = value

    if present("is_active"):
        value = data.get("is_active", True)
        if not isinstance(value, bool):
            errors["is_active"] = "is_active must be a boolean."
        else:
            out["is_active"] = value

    if present("type_id"):
        value = _parse_int(data.get("type_id"), "type_id", errors)
        if "type_id" not in errors:
            if value is None:
                errors["type_id"] = "Type id is required."
            else:
                out["type_id"] = value

    for field in ("mother_id", "father_id"):
        if present(field):
            if field in data:
                out[field] = _parse_int(data.get(field), field, errors)
            elif not partial:
                out[field] = None

    if errors:
        raise ValidationError("Invalid animal data.", errors=errors)
    return out


def parse_animal_type_payload(data, partial=False):
    """Validate and normalize an animal-type create/update payload."""
    errors = {}
    out = {}

    if not partial or "name" in data:
        out["name"] = _trim_string(
            data.get("name"), "name", MAX_TYPE_NAME_LEN, errors, required=True
        )
    if not partial or "description" in data:
        value = data.get("description")
        if value is not None and not isinstance(value, str):
            errors["description"] = "description must be a string."
        else:
            out["description"] = value

    if errors:
        raise ValidationError("Invalid animal type data.", errors=errors)
    return out


def _descendant_ids(db, animal_id):
    """Return ids of all animals that descend from ``animal_id``."""
    descendants = set()
    frontier = [animal_id]
    while frontier:
        rows = (
            db.query(Animal.id)
            .filter((Animal.mother_id.in_(frontier)) | (Animal.father_id.in_(frontier)))
            .all()
        )
        frontier = [row[0] for row in rows if row[0] not in descendants]
        descendants.update(frontier)
    return descendants


def _offspring_roles(db, animal_id):
    """Return (mother_count, father_count) of direct offspring references."""
    mother_count = db.query(Animal).filter(Animal.mother_id == animal_id).count()
    father_count = db.query(Animal).filter(Animal.father_id == animal_id).count()
    return mother_count, father_count


def validate_lineage(db, animal, proposed, errors):
    """Validate parent links and derived invariants for an animal.

    Args:
        db: database session.
        animal: existing Animal being updated, or None on create.
        proposed: dict with the *effective* post-change values for
            ``type_id``, ``gender``, ``date_of_birth``, ``mother_id`` and
            ``father_id`` (id may be int or None).
        errors: dict to collect field-keyed error messages into (mutated).
    """
    mother_id = proposed.get("mother_id")
    father_id = proposed.get("father_id")
    child_type_id = proposed.get("type_id")
    child_dob = proposed.get("date_of_birth")
    self_id = animal.id if animal is not None else None

    mother = db.get(Animal, mother_id) if mother_id else None
    father = db.get(Animal, father_id) if father_id else None

    if mother_id and mother is None:
        errors["mother_id"] = f"Mother with ID {mother_id} not found."
    if father_id and father is None:
        errors["father_id"] = f"Father with ID {father_id} not found."

    if mother_id and father_id and mother_id == father_id:
        errors["father_id"] = "Mother and father cannot be the same animal."

    for field, parent, expected_gender, role in (
        ("mother_id", mother, Gender.FEMALE, "mother"),
        ("father_id", father, Gender.MALE, "father"),
    ):
        if parent is None:
            continue
        if parent.id == self_id:
            errors[field] = f"An animal cannot be its own {role}."
            continue
        if parent.gender != expected_gender:
            errors[field] = f"The {role} must be {expected_gender}."
            continue
        if parent.type_id != child_type_id:
            errors[field] = (
                f"The {role} must belong to the same category " "as the animal."
            )
        if child_dob and parent.date_of_birth and child_dob <= parent.date_of_birth:
            errors[field] = (
                f"Date of birth must be after the {role}'s "
                f"birth date ({parent.date_of_birth.isoformat()})."
            )

    if errors:
        return

    # Cycle detection: a proposed parent may not be a descendant of the animal.
    if self_id is not None and (mother_id or father_id):
        descendants = _descendant_ids(db, self_id)
        for field, parent_id in (("mother_id", mother_id), ("father_id", father_id)):
            if parent_id and parent_id in descendants:
                errors[field] = "This parent would create a circular " "ancestry."
    if errors:
        return

    # Reverse-edge checks: don't break existing children from the parent side.
    if animal is None:
        return

    mother_count, father_count = _offspring_roles(db, self_id)

    if "gender" in proposed and proposed["gender"] != animal.gender:
        if mother_count and proposed["gender"] != Gender.FEMALE:
            errors["gender"] = (
                "Cannot change gender: animal is recorded as "
                f"the mother of {mother_count} offspring."
            )
        elif father_count and proposed["gender"] != Gender.MALE:
            errors["gender"] = (
                "Cannot change gender: animal is recorded as "
                f"the father of {father_count} offspring."
            )

    if (
        "type_id" in proposed
        and proposed["type_id"] != animal.type_id
        and (mother_count or father_count or animal.mother_id or animal.father_id)
    ):
        errors["type_id"] = (
            "Cannot change the category of an animal that "
            "has recorded parents or offspring."
        )

    if (
        child_dob
        and (mother_count or father_count)
        and child_dob != animal.date_of_birth
    ):
        # Animal's DOB may not be on/after any of its children's DOBs.
        earliest_child_dob = (
            db.query(Animal.date_of_birth)
            .filter(
                ((Animal.mother_id == self_id) | (Animal.father_id == self_id)),
                Animal.date_of_birth.isnot(None),
            )
            .order_by(Animal.date_of_birth.asc())
            .first()
        )
        if earliest_child_dob and child_dob >= earliest_child_dob[0]:
            errors["date_of_birth"] = (
                "Date of birth cannot be on or after the birth date of a "
                f"recorded offspring ({earliest_child_dob[0].isoformat()})."
            )


def check_type_name_available(db, name, exclude_id=None):
    """Return True when *name* is unused (case-insensitive)."""
    from sqlalchemy import func

    query = db.query(AnimalType).filter(func.lower(AnimalType.name) == name.lower())
    if exclude_id is not None:
        query = query.filter(AnimalType.id != exclude_id)
    return db.query(query.exists()).scalar() is False
