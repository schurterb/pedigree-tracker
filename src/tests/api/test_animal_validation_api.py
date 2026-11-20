"""
API validation tests (ISSUE-001, 006-012, 014, 015, 022).

Covers the strict validation contract: all validation failures must be
400 with {"message", "errors": {field: ...}} and must never leak SQL or
exception internals.
"""
import pytest
from datetime import date, timedelta

from .conftest import API_TEST_PREFIX

FORBIDDEN_SUBSTRINGS = (
    "SELECT",
    "INSERT",
    "UPDATE animals",
    "sqlite",
    "Error)",
    "Traceback",
    "sqlalchemy",
)


def assert_clean_error_body(resp, forbidden=FORBIDDEN_SUBSTRINGS):
    """Assert a 4xx/5xx body carries no SQL or exception internals."""
    body = resp.data.decode("utf-8", "replace")
    for s in forbidden:
        assert s not in body, f"response leaks internals: {s!r} in {body[:300]}"


@pytest.fixture
def types(db_session):
    """Two animal types plus animals of the primary type.

    Returns a namespace of eager ids - request teardown closes the shared
    session, which detaches ORM objects, so tests must reference ids rather
    than lazily-loaded attributes after the first request.
    """
    from types import SimpleNamespace
    from app.models import AnimalType, Animal, Gender

    type_a = AnimalType(name="ValTypeA", description="primary")
    type_b = AnimalType(name="ValTypeB", description="secondary")
    db_session.add_all([type_a, type_b])
    db_session.flush()
    dam = Animal(
        identifier="V-DAM",
        gender=Gender.FEMALE,
        date_of_birth=date(2020, 1, 1),
        animal_type=type_a,
    )
    sire = Animal(
        identifier="V-SIRE",
        gender=Gender.MALE,
        date_of_birth=date(2020, 2, 1),
        animal_type=type_a,
    )
    cross = Animal(
        identifier="V-CROSS",
        gender=Gender.FEMALE,
        date_of_birth=date(2020, 1, 1),
        animal_type=type_b,
    )
    unknown = Animal(
        identifier="V-UNK",
        gender=Gender.UNKNOWN,
        date_of_birth=date(2020, 1, 1),
        animal_type=type_a,
    )
    db_session.add_all([dam, sire, cross, unknown])
    db_session.commit()
    return SimpleNamespace(
        type_a=type_a.id,
        type_b=type_b.id,
        dam=dam.id,
        sire=sire.id,
        cross=cross.id,
        unknown=unknown.id,
    )


def create(client, **kwargs):
    data = {
        "identifier": "V-NEW",
        "type_id": kwargs.pop("type_id"),
        "gender": kwargs.pop("gender", "female"),
    }
    data.update(kwargs)
    return client.post(f"{API_TEST_PREFIX}/animals/", json=data)


# --- DOB handling (ISSUE-001, 009) ------------------------------------------


def test_create_without_dob(client, db_session, types):
    resp = create(client, type_id=types.type_a)
    assert resp.status_code == 201
    assert resp.json["date_of_birth"] is None


@pytest.mark.parametrize("dob", [None, ""])
def test_create_null_or_empty_dob(client, db_session, types, dob):
    resp = create(client, type_id=types.type_a, date_of_birth=dob)
    assert resp.status_code == 201
    assert resp.json["date_of_birth"] is None
    assert_clean_error_body(resp)


def test_create_malformed_dob(client, db_session, types):
    resp = create(client, type_id=types.type_a, date_of_birth="not-a-date")
    assert resp.status_code == 400
    assert "date_of_birth" in resp.json["errors"]
    assert_clean_error_body(resp)


def test_create_future_dob(client, db_session, types):
    future = (date.today() + timedelta(days=365)).isoformat()
    resp = create(client, type_id=types.type_a, date_of_birth=future)
    assert resp.status_code == 400
    assert "date_of_birth" in resp.json["errors"]


# --- identifier (ISSUE-010, 012) --------------------------------------------


@pytest.mark.parametrize("identifier", [None, "", "   "])
def test_create_blank_identifier_rejected(client, db_session, types, identifier):
    resp = create(client, type_id=types.type_a, identifier=identifier)
    assert resp.status_code == 400
    assert "identifier" in resp.json["errors"]
    assert_clean_error_body(resp)


def test_create_missing_identifier_rejected(client, db_session, types):
    resp = client.post(
        f"{API_TEST_PREFIX}/animals/",
        json={"type_id": types.type_a, "gender": "female"},
    )
    assert resp.status_code == 400
    assert "identifier" in resp.json["errors"]


def test_identifier_trimmed(client, db_session, types):
    resp = create(client, type_id=types.type_a, identifier="  V-TRIM  ")
    assert resp.status_code == 201
    assert resp.json["identifier"] == "V-TRIM"


def test_identifier_too_long(client, db_session, types):
    resp = create(client, type_id=types.type_a, identifier="X" * 51)
    assert resp.status_code == 400
    assert "identifier" in resp.json["errors"]


# --- other scalar fields (ISSUE-010) ----------------------------------------


def test_invalid_gender_rejected(client, db_session, types):
    resp = create(client, type_id=types.type_a, gender="banana")
    assert resp.status_code == 400
    assert "gender" in resp.json["errors"]


def test_malformed_json_rejected(client, db_session):
    resp = client.post(
        f"{API_TEST_PREFIX}/animals/", data="{not json", content_type="application/json"
    )
    assert resp.status_code == 400
    assert_clean_error_body(resp)


def test_non_object_body_rejected(client, db_session):
    resp = client.post(f"{API_TEST_PREFIX}/animals/", json=[1, 2, 3])
    assert resp.status_code == 400


# --- parent gender/type (ISSUE-006, 007) ------------------------------------


def test_male_as_mother_rejected(client, db_session, types):
    resp = create(client, type_id=types.type_a, mother_id=types.sire)
    assert resp.status_code == 400
    assert "mother_id" in resp.json["errors"]


def test_female_as_father_rejected(client, db_session, types):
    resp = create(client, type_id=types.type_a, father_id=types.dam)
    assert resp.status_code == 400
    assert "father_id" in resp.json["errors"]


@pytest.mark.parametrize("slot", ["mother_id", "father_id"])
def test_unknown_gender_parent_rejected(client, db_session, types, slot):
    resp = create(client, type_id=types.type_a, **{slot: types.unknown})
    assert resp.status_code == 400
    assert slot in resp.json["errors"]


def test_cross_type_parent_rejected(client, db_session, types):
    resp = create(client, type_id=types.type_a, mother_id=types.cross)
    assert resp.status_code == 400
    assert "mother_id" in resp.json["errors"]


def test_same_animal_as_both_parents_rejected(client, db_session, types):
    resp = create(
        client, type_id=types.type_a, mother_id=types.dam, father_id=types.dam
    )
    assert resp.status_code == 400


def test_nonexistent_parent_rejected(client, db_session, types):
    resp = create(client, type_id=types.type_a, mother_id=999999)
    assert resp.status_code == 400
    assert "mother_id" in resp.json["errors"]


def test_valid_parentage_accepted(client, db_session, types):
    resp = create(
        client,
        type_id=types.type_a,
        mother_id=types.dam,
        father_id=types.sire,
        date_of_birth="2024-01-01",
    )
    assert resp.status_code == 201
    assert resp.json["mother_id"] == types.dam
    assert resp.json["father_id"] == types.sire


# --- chronology (ISSUE-008) --------------------------------------------------


def test_child_predating_parents_rejected(client, db_session, types):
    resp = create(
        client,
        type_id=types.type_a,
        date_of_birth="2010-01-01",
        mother_id=types.dam,
        father_id=types.sire,
    )
    assert resp.status_code == 400
    assert "mother_id" in resp.json["errors"]
    assert "father_id" in resp.json["errors"]


def test_child_dob_equal_parent_rejected(client, db_session, types):
    resp = create(
        client, type_id=types.type_a, date_of_birth="2020-01-01", mother_id=types.dam
    )
    assert resp.status_code == 400


# --- uniqueness scope (ISSUE-014) --------------------------------------------


def test_identifier_unique_within_type(client, db_session, types):
    resp = create(client, type_id=types.type_a, identifier="V-DAM")
    assert resp.status_code == 409
    resp2 = create(client, type_id=types.type_b, identifier="V-DAM")
    assert resp2.status_code == 201


# --- cycles and self-parenting (ISSUE-011) -----------------------------------


def test_self_parent_rejected(client, db_session, types):
    resp = client.put(
        f"{API_TEST_PREFIX}/animals/{types.dam}", json={"mother_id": types.dam}
    )
    assert resp.status_code == 400
    assert "mother_id" in resp.json["errors"]
    assert_clean_error_body(resp)


def test_two_node_cycle_rejected(client, db_session, types):
    """Setting a parent of an existing child must 400, not 500."""
    resp = client.put(
        f"{API_TEST_PREFIX}/animals/{types.dam}", json={"mother_id": types.sire}
    )
    assert resp.status_code == 400  # gender check fires first

    # create a proper child then try to invert the relationship
    child = create(
        client,
        type_id=types.type_a,
        identifier="V-CYC",
        mother_id=types.dam,
        father_id=types.sire,
        date_of_birth="2024-01-01",
    )
    assert child.status_code == 201
    child_id = child.json["id"]
    resp = client.put(
        f"{API_TEST_PREFIX}/animals/{types.dam}", json={"mother_id": child_id}
    )
    assert resp.status_code == 400
    assert "mother_id" in resp.json["errors"]
    # unchanged
    after = client.get(f"{API_TEST_PREFIX}/animals/{types.dam}").json
    assert after["mother_id"] is None


def test_clear_parent_with_null(client, db_session, types):
    child = create(
        client,
        type_id=types.type_a,
        identifier="V-CLR",
        mother_id=types.dam,
        father_id=types.sire,
        date_of_birth="2024-01-01",
    )
    child_id = child.json["id"]
    resp = client.put(f"{API_TEST_PREFIX}/animals/{child_id}", json={"mother_id": None})
    assert resp.status_code == 200
    assert resp.json["mother_id"] is None
    assert resp.json["father_id"] == types.sire


# --- reverse-edge checks ------------------------------------------------------


def test_parent_gender_change_blocked_by_offspring(client, db_session, types):
    create(
        client,
        type_id=types.type_a,
        identifier="V-GEO",
        mother_id=types.dam,
        father_id=types.sire,
        date_of_birth="2024-01-01",
    )
    resp = client.put(f"{API_TEST_PREFIX}/animals/{types.dam}", json={"gender": "male"})
    assert resp.status_code == 400
    assert "gender" in resp.json["errors"]


def test_parent_type_change_blocked_by_offspring(client, db_session, types):
    create(
        client,
        type_id=types.type_a,
        identifier="V-TCO",
        mother_id=types.dam,
        father_id=types.sire,
        date_of_birth="2024-01-01",
    )
    resp = client.put(
        f"{API_TEST_PREFIX}/animals/{types.dam}", json={"type_id": types.type_b}
    )
    assert resp.status_code == 400
    assert "type_id" in resp.json["errors"]


def test_parent_dob_change_blocked_by_offspring(client, db_session, types):
    create(
        client,
        type_id=types.type_a,
        identifier="V-DCO",
        mother_id=types.dam,
        father_id=types.sire,
        date_of_birth="2024-01-01",
    )
    resp = client.put(
        f"{API_TEST_PREFIX}/animals/{types.dam}", json={"date_of_birth": "2025-01-01"}
    )
    assert resp.status_code == 400
    assert "date_of_birth" in resp.json["errors"]


def test_notes_update_unaffected(client, db_session, types):
    resp = client.put(
        f"{API_TEST_PREFIX}/animals/{types.dam}", json={"notes": "plain notes update"}
    )
    assert resp.status_code == 200
    assert resp.json["notes"] == "plain notes update"


# --- pedigree depth (ISSUE-022) ------------------------------------------------


@pytest.mark.parametrize("gen", ["0", "-1"])
def test_pedigree_nonpositive_generations(client, db_session, types, gen):
    resp = client.get(
        f"{API_TEST_PREFIX}/animals/{types.dam}/pedigree?generations={gen}"
    )
    assert resp.status_code == 400
    assert_clean_error_body(resp)


def test_pedigree_generations_clamped(client, db_session, types):
    resp = client.get(f"{API_TEST_PREFIX}/animals/{types.dam}/pedigree?generations=6")
    assert resp.status_code == 200


def test_pedigree_generations_nonint(client, db_session, types):
    resp = client.get(f"{API_TEST_PREFIX}/animals/{types.dam}/pedigree?generations=abc")
    assert resp.status_code == 400
