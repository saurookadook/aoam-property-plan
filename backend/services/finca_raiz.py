from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Optional, cast

import requests
from bs4 import BeautifulSoup

from services.exceptions import FetchError, ScrapeError
from utils.logging.extended_logger import ExtendedLogger

logger = cast(ExtendedLogger, logging.getLogger(__name__))

HOST = "fincaraiz.com.co"

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
}
REQUEST_TIMEOUT = 30

# Finca Raiz only lists Colombian property, and neither the JSON-LD block nor the
# rendered markup names the country - so tiers 2 and 3 depend on this default.
COUNTRY = "Colombia"

# Every ``NOT NULL`` column on ``properties`` that has to come off the page.
# ``country`` and ``source_created_at`` are excluded because they are defaulted
# below; ``source_url`` is supplied by the caller and ``status`` is derived.
REQUIRED_FIELDS = (
    "address",
    "bedrooms",
    "city",
    "latitude",
    "longitude",
    "neighborhood",
    "property_type",
    "state",
)

# NOTE: the tag carries a ``crossorigin`` attribute, so the pattern has to allow
# attributes between the id and the closing ``>``.
_NEXT_DATA_PATTERN = re.compile(
    r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.DOTALL
)
_JSON_LD_PATTERN = re.compile(
    r'<script type="application/ld\+json"[^>]*>(.*?)</script>', re.DOTALL
)

# Kept in one place so a Finca Raiz redesign is a single-site fix.
_DOM_SELECTORS = {
    "description": ".property-description",
    "location_header": ".location-header .ant-col",
    "price": ".property-price-tag .main-price",
    "technical_sheet_row": ".technical-sheet .ant-row",
}

_TECHNICAL_SHEET_LABELS = {
    "Habitaciones": "bedrooms",
    "Tipo de Inmueble": "property_type",
}

_INTEGER_FIELDS = ("bedrooms",)


def fetch(url: str) -> str:
    """Retrieves a listing page. Raises ``FetchError`` if it cannot be read."""
    try:
        response = requests.get(
            url,
            headers=REQUEST_HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise FetchError(f"Could not fetch listing page at '{url}': {exc}") from exc

    return response.text


def parse_listing_html(html: str) -> dict[str, Any]:
    """
    Extracts a property payload from a Finca Raiz listing page.

    Three tiers are merged in order, first non-``None`` value winning:

      1. ``__NEXT_DATA__`` - the full record, including amenities and the
         publication date, neither of which appears anywhere else.
      2. JSON-LD - price, address and coordinates.
      3. Rendered markup - city, state, neighborhood, bedrooms, property type.

    ``ScrapeError`` is raised only when the merged result still leaves one of
    ``REQUIRED_FIELDS`` empty.

    NOTE: ``source_created_at`` is only ever available from tier 1. When a page
    falls through to tiers 2/3 it is defaulted to now and flagged in ``notes`` as
    ``source_created_at_inferred``, so a degraded parse still yields a
    persistable row rather than failing outright.
    """
    merged: dict[str, Any] = {}
    notes: dict[str, Any] = {}

    for parser in (_parse_next_data, _parse_json_ld, _parse_dom):
        parsed, parsed_notes = parser(html)
        for key, value in parsed.items():
            if merged.get(key) is None:
                merged[key] = value
        for key, value in parsed_notes.items():
            notes.setdefault(key, value)

    # Tiers 2 and 3 cannot see the ``hidePrice`` flag, so they will happily scrape
    # a price off a listing that hides one. Tier 1's status is authoritative.
    if merged.get("status") == "price_hidden":
        merged.pop("purchase_price_cop", None)

    missing = [field for field in REQUIRED_FIELDS if merged.get(field) is None]
    if missing:
        raise ScrapeError(
            f"Could not extract required field(s) from listing page: "
            f"{', '.join(missing)}"
        )

    merged.setdefault("country", COUNTRY)
    merged.setdefault("status", "active")
    merged.setdefault("amenities", [])

    if merged.get("source_created_at") is None:
        merged["source_created_at"] = datetime.now(timezone.utc)
        notes["source_created_at_inferred"] = True

    if notes:
        merged["notes"] = json.dumps(notes, ensure_ascii=False)

    return merged


def scrape(url: str) -> dict[str, Any]:
    """Fetches and parses a listing, returning a ``properties`` payload."""
    payload = parse_listing_html(fetch(url))
    payload["source_url"] = url
    return payload


def _parse_next_data(html: str) -> tuple[dict[str, Any], dict[str, Any]]:
    match = _NEXT_DATA_PATTERN.search(html)
    if match is None:
        logger.warning("No '__NEXT_DATA__' block found on Finca Raiz listing page")
        return {}, {}

    try:
        data = json.loads(match.group(1))["props"]["pageProps"]["data"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.warning(f"Could not read '__NEXT_DATA__' block: {exc}")
        return {}, {}

    locations = data.get("locations") or {}
    status = _extract_status(data)

    parsed = {
        "address": data.get("address"),
        "amenities": _extract_amenities(data),
        "bedrooms": data.get("bedrooms"),
        "city": _first_location_name(locations, "city"),
        "country": _first_location_name(locations, "country"),
        "description": data.get("description"),
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "name": data.get("title"),
        "neighborhood": (
            _first_location_name(locations, "neighbourhood")
            or _first_location_name(locations, "location_main")
        ),
        "property_type": (data.get("property_type") or {}).get("name"),
        # A hidden price is left unset on purpose - that is why
        # ``purchase_price_cop`` is nullable. ``status`` records why.
        "purchase_price_cop": (
            None
            if status == "price_hidden"
            else (data.get("price") or {}).get("amount")
        ),
        "source_created_at": data.get("created_at"),
        "state": _first_location_name(locations, "state"),
        "status": status,
    }

    notes = {
        "bathrooms": data.get("bathrooms"),
        "common_expenses_cop": (data.get("commonExpenses") or {}).get("amount"),
        "m2": data.get("m2"),
        "stratum": data.get("stratum"),
    }

    return _drop_empty(parsed), _drop_empty(notes)


def _parse_json_ld(html: str) -> tuple[dict[str, Any], dict[str, Any]]:
    for raw_block in _JSON_LD_PATTERN.findall(html):
        try:
            block = json.loads(raw_block)
        except json.JSONDecodeError:
            continue

        if not isinstance(block, dict):
            continue

        # NOTE: ``@type`` is unreliable - sale listings are tagged ``RentAction`` -
        # so the block is identified by shape rather than by its declared type.
        price_specification = block.get("priceSpecification") or {}
        listed_object = block.get("object") or {}
        geo = listed_object.get("geo") or {}

        if not (price_specification or geo):
            continue

        parsed = {
            "address": listed_object.get("address"),
            "description": block.get("description"),
            "latitude": geo.get("latitude"),
            "longitude": geo.get("longitude"),
            "name": block.get("name"),
            "purchase_price_cop": (
                price_specification.get("price")
                if price_specification.get("priceCurrency") == "COP"
                else None
            ),
        }

        parsed = _drop_empty(parsed)
        if parsed:
            return parsed, {}

    return {}, {}


def _parse_dom(html: str) -> tuple[dict[str, Any], dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")

    parsed: dict[str, Any] = {
        "description": _text_or_none(soup.select_one(_DOM_SELECTORS["description"])),
        "purchase_price_cop": _parse_price(
            _text_or_none(soup.select_one(_DOM_SELECTORS["price"]))
        ),
    }
    parsed.update(_parse_location_header(soup))
    parsed.update(_parse_technical_sheet(soup))

    return _drop_empty(parsed), {}


def _parse_location_header(soup: BeautifulSoup) -> dict[str, Any]:
    """
    The header renders the location as a single "neighborhood, city, state" line
    under a "Ubicación Principal" label.
    """
    column = soup.select_one(_DOM_SELECTORS["location_header"])
    if column is None:
        return {}

    paragraphs = [_text_or_none(p) for p in column.select("p")]
    values = [text for text in paragraphs if text and "Ubicaci" not in text]
    if not values:
        return {}

    parts = [part.strip() for part in values[0].split(",") if part.strip()]
    if len(parts) < 3:
        return {}

    return {"neighborhood": parts[0], "city": parts[1], "state": parts[2]}


def _parse_technical_sheet(soup: BeautifulSoup) -> dict[str, Any]:
    parsed: dict[str, Any] = {}

    for row in soup.select(_DOM_SELECTORS["technical_sheet_row"]):
        labels = [
            text
            for text in (_text_or_none(span) for span in row.select("span"))
            if text and text != "•"
        ]
        if not labels:
            continue

        field = _TECHNICAL_SHEET_LABELS.get(labels[0])
        if field is None:
            continue

        value_element = row.select_one("[title]")
        value = (
            value_element.get("title")
            if value_element is not None
            else _text_or_none(row.select_one("strong"))
        )
        if not value:
            continue

        if field in _INTEGER_FIELDS:
            digits = re.sub(r"\D", "", str(value))
            parsed[field] = int(digits) if digits else None
        else:
            parsed[field] = str(value).strip()

    return parsed


def _extract_status(data: dict[str, Any]) -> str:
    if data.get("hidePrice"):
        return "price_hidden"
    if data.get("sold"):
        return "sold"
    if data.get("active") is False:
        return "inactive"
    return "active"


def _extract_amenities(data: dict[str, Any]) -> list[str]:
    if data.get("facilitiesNotApply"):
        return []

    return [
        facility["name"]
        for facility in (data.get("facilities") or [])
        if isinstance(facility, dict) and facility.get("name")
    ]


def _first_location_name(locations: dict[str, Any], key: str) -> Optional[str]:
    entries = locations.get(key) or []
    if isinstance(entries, dict):
        entries = [entries]

    for entry in entries:
        name = (entry or {}).get("name")
        if name:
            return name

    return None


def _parse_price(price_text: Optional[str]) -> Optional[float]:
    """Turns a rendered price like ``$ 700.000.000`` into ``700000000.0``."""
    if not price_text:
        return None

    digits = re.sub(r"\D", "", price_text)

    return float(digits) if digits else None


def _text_or_none(element: Any) -> Optional[str]:
    if element is None:
        return None

    text = element.get_text(" ", strip=True)

    return text or None


def _drop_empty(values: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in values.items() if value is not None}
