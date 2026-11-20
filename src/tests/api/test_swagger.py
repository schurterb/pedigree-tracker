"""
Swagger schema and docs rendering tests (ISSUE-016).
"""
from .conftest import API_TEST_PREFIX


def test_swagger_json_renders(client, db_session):
    resp = client.get(f"{API_TEST_PREFIX}/swagger.json")
    assert resp.status_code == 200
    schema = resp.json
    assert "paths" in schema
    assert any(
        "/animals/{id}" in p for p in schema["paths"]
    ), "animal item path missing from schema"
    assert "definitions" in schema
    assert "AnimalInput" in schema["definitions"]


def test_docs_page_loads(client, db_session):
    resp = client.get(f"{API_TEST_PREFIX}/docs")
    assert resp.status_code == 200
    assert b"swagger" in resp.data.lower()
