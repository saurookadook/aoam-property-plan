from __future__ import annotations

import json
import gzip
import re
from pathlib import Path
from typing import Any

import pytest

from services import finca_raiz

FIXTURES_DIR = Path(__file__).parent / "fixtures"

_JSON_LD_BLOCK = r'<script type="application/ld\+json".*?</script>'
_NEXT_DATA_BLOCK = r'<script id="__NEXT_DATA__".*?</script>'


@pytest.fixture(scope="session")
def finca_raiz_html() -> str:
    """
    A real Finca Raiz listing page - the Salento house at
    https://www.fincaraiz.com.co/casa-en-venta-en-ahitamara-salento/193301244
    """
    with gzip.open(
        FIXTURES_DIR / "finca_raiz_salento.html.gz", "rt", encoding="utf-8"
    ) as gz:
        return gz.read()


@pytest.fixture
def finca_raiz_html_without_next_data(finca_raiz_html: str) -> str:
    """Exercises tier 2 + tier 3: JSON-LD and the rendered markup."""
    return re.sub(_NEXT_DATA_BLOCK, "", finca_raiz_html, flags=re.DOTALL)


@pytest.fixture
def finca_raiz_html_dom_only(finca_raiz_html_without_next_data: str) -> str:
    """Exercises tier 3 alone: no embedded JSON of any kind."""
    return re.sub(
        _JSON_LD_BLOCK, "", finca_raiz_html_without_next_data, flags=re.DOTALL
    )


@pytest.fixture
def override_next_data():
    """
    Rewrites keys on ``props.pageProps.data`` in the fixture's ``__NEXT_DATA__``
    block, for cases the saved page does not itself cover (sold, hidden price...).
    """

    def _override(html: str, **overrides: Any) -> str:
        match = finca_raiz._NEXT_DATA_PATTERN.search(html)
        assert match is not None, "fixture is missing its '__NEXT_DATA__' block"

        payload = json.loads(match.group(1))
        payload["props"]["pageProps"]["data"].update(overrides)

        return html[: match.start(1)] + json.dumps(payload) + html[match.end(1) :]

    return _override
