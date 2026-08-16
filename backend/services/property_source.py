from __future__ import annotations

from typing import Any, Callable
from urllib.parse import urlparse

from services import finca_raiz
from services.exceptions import UnsupportedSource

# Adding a source (metrocuadrado.com, fincainca.com) is a new module plus one
# entry here - the resolver and the calling route stay untouched.
_PARSERS: dict[str, Callable[[str], dict[str, Any]]] = {
    finca_raiz.HOST: finca_raiz.parse_listing_html,
}

_FETCHERS: dict[str, Callable[[str], str]] = {
    finca_raiz.HOST: finca_raiz.fetch,
}


def resolve_host(url: str) -> str:
    """Normalises a URL's host: strips any port and a leading ``www.``."""
    netloc = urlparse(url or "").netloc.lower()

    return netloc.split("@")[-1].split(":")[0].removeprefix("www.")


def supported_hosts() -> tuple[str, ...]:
    return tuple(sorted(_PARSERS))


def parse(url: str, html: str) -> dict[str, Any]:
    """Parses a listing page using the parser registered for the URL's host."""
    return _get(_PARSERS, url)(html)


def scrape(url: str) -> dict[str, Any]:
    """Fetches and parses a listing, returning a ``properties`` payload."""
    html = _get(_FETCHERS, url)(url)
    payload = parse(url, html)
    payload["source_url"] = url

    return payload


def _get(registry: dict[str, Any], url: str) -> Any:
    host = resolve_host(url)
    handler = registry.get(host)

    if handler is None:
        raise UnsupportedSource(
            f"No parser registered for host '{host}' "
            f"(supported: {', '.join(supported_hosts())})"
        )

    return handler
