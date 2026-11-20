"""
Session/pool lifecycle regression test (ISSUE-018).

Reproduces the original failure mode: with GC disabled, a run of failing
requests used to leave pooled connections checked out until the QueuePool
was exhausted. The request-scoped session teardown must return every
connection deterministically.
"""
import gc

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

import app.database as app_db
from app.models import Base, AnimalType, Animal, Gender
from .conftest import API_TEST_PREFIX


@pytest.fixture
def isolated_db(app, monkeypatch, tmp_path):
    """Point app.database.SessionLocal at a private file-backed engine."""
    engine = create_engine(
        f"sqlite:///{tmp_path}/pool.db", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    registry = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )
    monkeypatch.setattr(app_db, "SessionLocal", registry)
    yield engine, registry
    registry.remove()
    engine.dispose()


def test_failing_requests_do_not_leak_connections(app, client, isolated_db):
    engine, registry = isolated_db

    # Seed fixtures through the same registry
    session = registry()
    atype = AnimalType(name="PoolType", description="pool test")
    session.add(atype)
    session.flush()
    dam = Animal(identifier="P-DAM", gender=Gender.FEMALE, animal_type=atype)
    session.add(dam)
    session.commit()
    type_id, dam_id = atype.id, dam.id
    session.close()

    assert engine.pool.checkedout() == 0

    gc_was_enabled = gc.isenabled()
    gc.disable()
    try:
        for i in range(10):
            # Validation failure (400)
            r = client.post(
                f"{API_TEST_PREFIX}/animals/",
                json={"identifier": "", "type_id": type_id, "gender": "female"},
            )
            assert r.status_code == 400
            # 404
            r = client.get(f"{API_TEST_PREFIX}/animals/999999")
            assert r.status_code == 404
            # Self-parent / cycle-style rejection (400 now, 500 pre-fix)
            r = client.put(
                f"{API_TEST_PREFIX}/animals/{dam_id}", json={"mother_id": dam_id}
            )
            assert r.status_code == 400
            assert engine.pool.checkedout() == 0, f"connection leaked after request {i}"
    finally:
        if gc_was_enabled:
            gc.enable()

    # A normal write still completes quickly afterwards
    r = client.post(
        f"{API_TEST_PREFIX}/animals/",
        json={"identifier": "P-OK", "type_id": type_id, "gender": "female"},
    )
    assert r.status_code == 201
    assert engine.pool.checkedout() == 0
