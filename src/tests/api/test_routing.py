"""
Trailing-slash route contract tests (ISSUE-002/017).

Every route must respond identically with and without a trailing slash,
without redirects.
"""
import pytest

from .conftest import API_TEST_PREFIX


@pytest.fixture
def type_and_animal(db_session):
    """One type plus a female animal and a male animal of that type."""
    from app.models import AnimalType, Animal, Gender

    atype = AnimalType(name="RouteType", description="routing")
    db_session.add(atype)
    db_session.flush()
    mother = Animal(identifier="RT-MOM", gender=Gender.FEMALE, animal_type=atype)
    father = Animal(identifier="RT-DAD", gender=Gender.MALE, animal_type=atype)
    child = Animal(
        identifier="RT-KID",
        gender=Gender.FEMALE,
        animal_type=atype,
        mother_id=mother.id,
        father_id=father.id,
    )
    db_session.add_all([mother, father])
    db_session.flush()
    db_session.add(child)
    db_session.commit()
    return atype, mother, father, child


def test_collection_routes_both_slashes(client, db_session):
    for path in ("animals", "animal-types"):
        for suffix in ("/", ""):
            resp = client.get(f"{API_TEST_PREFIX}/{path}{suffix}")
            assert resp.status_code == 200, f"{path}{suffix} -> {resp.status_code}"


def test_item_routes_both_slashes(client, db_session, type_and_animal):
    _, mother, _, child = type_and_animal
    paths = [
        f"animals/{mother.id}",
        f"animals/{child.id}/pedigree",
        f"animals/{mother.id}/offspring",
        f"animal-types/{mother.type_id}",
        f"animal-types/{mother.type_id}/potential-parents",
    ]
    for path in paths:
        for suffix in ("/", ""):
            resp = client.get(f"{API_TEST_PREFIX}/{path}{suffix}")
            assert resp.status_code == 200, f"{path}{suffix} -> {resp.status_code}"


def test_docs_both_slashes(client, db_session):
    for suffix in ("", "/"):
        resp = client.get(f"{API_TEST_PREFIX}/docs{suffix}")
        assert resp.status_code == 200


def test_post_no_slash_no_redirect(client, db_session, type_and_animal):
    """strict_slashes=False must route POST /animals without a 308."""
    atype, *_ = type_and_animal
    resp = client.post(
        f"{API_TEST_PREFIX}/animals",
        json={"identifier": "RT-NOSLASH", "type_id": atype.id, "gender": "female"},
    )
    assert resp.status_code == 201
