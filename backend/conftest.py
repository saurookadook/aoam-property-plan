from __future__ import annotations

import os

import pytest
import requests_mock
from alembic import command, config
from sqlalchemy.exc import InvalidRequestError
from starlette.testclient import TestClient

from _mocks.temporal import get_mock_utcnow
from db.db_session_manager import DBSessionManager


def pytest_sessionstart(session):
    os.environ["DATABASE_NAME"] = "test_aoam_property_plan"

    alembic_ini = os.path.join(os.path.abspath("."), "alembic.ini")
    alembic_config = config.Config(alembic_ini)
    command.upgrade(alembic_config, "head")


@pytest.fixture(autouse=True)
def test_db_session():
    db_session_manager = DBSessionManager()
    _test_engine = db_session_manager.engine
    _test_db_session = db_session_manager.scoped_session

    with _test_engine.connect() as db_connection:
        transaction = db_connection.begin()
        try:
            yield _test_db_session(bind=db_connection)
        except InvalidRequestError as e:
            raise InvalidRequestError(
                str(e) + " Make sure you're using `_test_db_session` correctly!"
            )
        transaction.rollback()
        db_connection.close()
    _test_db_session.remove()


@pytest.fixture
def mock_utcnow():
    return get_mock_utcnow()


@pytest.fixture(autouse=True)
def patch_utcnow(mocker):
    mock_datetime = mocker.patch("datetime.datetime", autospec=True)
    mock_datetime.now.return_value = get_mock_utcnow()
    return mock_datetime
