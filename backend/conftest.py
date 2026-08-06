from __future__ import annotations

import os
from datetime import datetime

import pytest
import requests_mock
from alembic import command, config
from sqlalchemy.exc import InvalidRequestError
from starlette.testclient import TestClient

from _mocks.temporal import get_mock_utcnow
from api.app.main import app
from api.dependencies.db_session import api_db_session
from config.env_var_manager import EnvVarManager
from db.db_session_manager import DBSessionManager

os.environ["FORCE_COLOR"] = "1"
os.environ["PYTHONUNBUFFERED"] = "1"


def pytest_sessionstart(session):
    import shutil

    raw_window_width, raw_window_height = shutil.get_terminal_size()
    os.environ["COLUMNS"] = str(raw_window_width)
    os.environ["LINES"] = str(raw_window_height)

    EnvVarManager().env_vars.database_name = os.environ["DATABASE_NAME"] = (
        "test_aoam_property_plan"
    )

    alembic_ini = os.path.join(os.path.abspath("."), "alembic.ini")
    alembic_config = config.Config(alembic_ini)
    command.upgrade(alembic_config, "head")


@pytest.fixture
def http_requests_mock():
    with requests_mock.Mocker(real_http=False) as mock:
        yield mock


@pytest.fixture(autouse=True)
def test_db_session():
    db_session_manager = DBSessionManager()
    _test_engine = db_session_manager.engine
    _test_db_session = db_session_manager.scoped_session

    with _test_engine.connect() as db_connection:
        with db_connection.begin() as transaction:
            try:
                yield _test_db_session(bind=db_connection)
            except InvalidRequestError as e:
                raise InvalidRequestError(
                    str(e) + " Make sure you're using `_test_db_session` correctly!"
                )
            transaction.rollback()
            db_connection.close()
    _test_db_session.remove()


@pytest.fixture()
def test_app_client(test_db_session):
    app.dependency_overrides[api_db_session] = lambda: test_db_session
    return TestClient(app, base_url="https://aoam.dev")


@pytest.fixture(scope="class")
def test_app_client_lifecycle(test_db_session):
    app.dependency_overrides[api_db_session] = lambda: test_db_session
    with TestClient(app, base_url="https://aoam.dev") as client:
        yield client
    app.dependency_overrides.pop(api_db_session, None)


@pytest.fixture
def mock_utcnow() -> datetime:
    return get_mock_utcnow()


@pytest.fixture(autouse=True)
def patch_utcnow(mocker):
    mock_datetime = mocker.patch("datetime.datetime")
    mock_datetime.now.return_value = get_mock_utcnow()
    return mock_datetime


@pytest.fixture
def markets_data() -> list[dict[str, str | None]]:
    return [
        {
            "country": "Colombia",
            "region": "Valle del Cauca",
            "locality": "Calima",
            "district": None,
        },
        {
            "country": "Colombia",
            "region": "Valle del Cauca",
            "locality": "Pance",
            "district": None,
        },
        {
            "country": "Colombia",
            "region": "Quindío",
            "locality": "Salento",
            "district": None,
        },
        {
            "country": "Colombia",
            "region": "RAP (Especial) Central",
            "locality": "Bogota Capital District - Municipality",
            "district": "Bogota",
        },
    ]
