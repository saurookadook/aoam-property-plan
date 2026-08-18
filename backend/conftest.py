from __future__ import annotations

import gzip
import json
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
from constants import AIRROI_BASE_URL
from db.db_session_manager import DBSessionManager
from utils.filesystem import get_module_root, get_project_root

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


@pytest.fixture(scope="session")
def finca_raiz_html() -> str:
    """
    A real Finca Raiz listing page - the Salento house at
    https://www.fincaraiz.com.co/casa-en-venta-en-ahitamara-salento/193301244
    """
    fixtures_dir = get_module_root(__file__) / "_fixtures" / "html"

    with gzip.open(
        fixtures_dir / "finca_raiz_salento.html.gz", "rt", encoding="utf-8"
    ) as gz:
        return gz.read()


@pytest.fixture
def mock_utcnow() -> datetime:
    return get_mock_utcnow()


@pytest.fixture(autouse=True)
def patch_utcnow(mocker):
    mock_datetime = mocker.patch("datetime.datetime")
    mock_datetime.now.return_value = get_mock_utcnow()
    return mock_datetime


@pytest.fixture(scope="session")
def airroi_estimate_captures() -> dict[tuple[float, float, int], dict]:
    """
    The six real ``/calculator/estimate`` responses saved under ``_research/``.

    Keyed by the query that produced them: coordinates plus bedroom count. That
    tuple is unique across the set - each of the three localities was captured
    twice, at two sizes - so a test can ask for "Calima, 2 bedrooms" without
    naming a file.

    The bedroom count only exists in the filename; the response echoes the
    coordinates back under ``location`` but never the size it was asked about.
    """
    captures_dir = get_project_root(__file__) / "_research" / "calculator" / "estimate"
    captures: dict[tuple[float, float, int], dict] = {}

    for capture_file in sorted(captures_dir.glob("*.json")):
        with open(capture_file, "r") as capture_json:
            capture = json.load(capture_json)

        # ``salento_quindio_colombia__2-baths_3-bedrooms_8-guests`` -> 3
        bedrooms = int(capture_file.stem.split("__")[1].split("_")[1].split("-")[0])
        location = capture["location"]

        captures[
            (
                round(location["latitude"], 4),
                round(location["longitude"], 4),
                bedrooms,
            )
        ] = capture

    return captures


@pytest.fixture
def airroi_estimate_dynamic_resp_callback(airroi_estimate_captures):
    """Serves whichever capture matches the coordinates and size asked for."""

    def _matcher(request, context):
        query = request.qs

        try:
            capture_key = (
                round(float(query["lat"][0]), 4),
                round(float(query["lng"][0]), 4),
                int(float(query["bedrooms"][0])),
            )
        except (KeyError, IndexError, ValueError):
            context.status_code = 400
            return {}

        capture = airroi_estimate_captures.get(capture_key)

        if capture is None:
            context.status_code = 404
            return {}

        context.status_code = 200
        return capture

    return _matcher


@pytest.fixture
def airroi_estimate_mock(http_requests_mock, airroi_estimate_dynamic_resp_callback):
    """
    Registers ``GET /calculator/estimate`` against the saved captures.

    The root mocker runs with ``real_http=False``, so a test that reaches AirROI
    without this fixture fails rather than making a paid call.
    """
    return http_requests_mock.get(
        f"{AIRROI_BASE_URL}/calculator/estimate",
        json=airroi_estimate_dynamic_resp_callback,
    )


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
