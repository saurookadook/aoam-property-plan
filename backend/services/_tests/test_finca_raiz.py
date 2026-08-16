from __future__ import annotations

import json

import pytest
import requests

from services import finca_raiz
from services.exceptions import FetchError, ScrapeError

LISTING_URL = (
    "https://www.fincaraiz.com.co/casa-en-venta-en-ahitamara-salento/193301244"
)


class TestParseListingHtml:
    def test_extracts_full_record_from_next_data(self, finca_raiz_html):
        result = finca_raiz.parse_listing_html(finca_raiz_html)

        assert result["address"] == "CASA 1 MZ B/AHITAMARA/EL LIMONAR"
        assert result["bedrooms"] == 5
        assert result["city"] == "Salento"
        assert result["country"] == "Colombia"
        assert result["latitude"] == 4.57076
        assert result["longitude"] == -75.640629
        assert result["name"] == "Casa en Venta en Ahitamara, Salento"
        assert result["neighborhood"] == "Ahitamara"
        assert result["property_type"] == "Casa"
        assert result["purchase_price_cop"] == 700000000
        assert result["source_created_at"] == "2026-01-21T00:00:00+00:00"
        assert result["state"] == "Quindio"
        assert result["status"] == "active"
        assert result["description"].startswith("Código ***")

    def test_amenities_come_from_facilities_not_technical_sheet(self, finca_raiz_html):
        """
        ``facilities`` is the amenity list. ``technicalSheet`` is the
        "Detalles de la Propiedad" spec table and belongs in ``notes``.
        """
        result = finca_raiz.parse_listing_html(finca_raiz_html)

        assert result["amenities"] == ["Patio", "Servicios Públicos"]

    def test_does_not_use_the_sites_own_usd_price(self, finca_raiz_html):
        """
        Finca Raiz publishes ``price_amount_usd`` (217599) using a ~3216 COP/USD
        rate. USD has to be derived from our own rate instead, so the scraper must
        not surface theirs.
        """
        result = finca_raiz.parse_listing_html(finca_raiz_html)

        assert "purchase_price_usd" not in result
        assert 217599 not in result.values()

    def test_notes_capture_calculation_engine_inputs(self, finca_raiz_html):
        result = finca_raiz.parse_listing_html(finca_raiz_html)

        assert json.loads(result["notes"]) == {
            "bathrooms": 4,
            "common_expenses_cop": 0,
            "m2": 173,
            "stratum": 3,
        }


class TestParseListingHtmlTierFallback:
    def test_json_ld_and_dom_still_yield_a_persistable_record(
        self, finca_raiz_html_without_next_data
    ):
        result = finca_raiz.parse_listing_html(finca_raiz_html_without_next_data)

        # from JSON-LD
        assert result["address"] == "CASA 1 MZ B/AHITAMARA/EL LIMONAR"
        assert result["latitude"] == 4.57076
        assert result["longitude"] == -75.640629
        assert result["purchase_price_cop"] == 700000000
        # from the rendered markup
        assert result["city"] == "Salento"
        assert result["state"] == "Quindio"
        assert result["neighborhood"] == "Ahitamara"
        assert result["bedrooms"] == 5
        assert result["property_type"] == "Casa"
        # site-level default - the country appears nowhere on the page
        assert result["country"] == "Colombia"

    def test_amenities_are_empty_without_next_data(
        self, finca_raiz_html_without_next_data
    ):
        """
        ``facilities`` is client-rendered, so a degraded parse cannot recover
        amenities. An empty list here means "not recoverable", NOT "no amenities" -
        this assertion exists so that distinction is not quietly "fixed" later.
        """
        result = finca_raiz.parse_listing_html(finca_raiz_html_without_next_data)

        assert result["amenities"] == []

    def test_source_created_at_is_inferred_and_flagged_without_next_data(
        self, finca_raiz_html_without_next_data
    ):
        result = finca_raiz.parse_listing_html(finca_raiz_html_without_next_data)

        assert result["source_created_at"] is not None
        assert json.loads(result["notes"])["source_created_at_inferred"] is True

    def test_raises_when_dom_alone_cannot_fill_required_fields(
        self, finca_raiz_html_dom_only
    ):
        """The address and coordinates live only in JSON-LD and ``__NEXT_DATA__``."""
        with pytest.raises(ScrapeError) as exc_info:
            finca_raiz.parse_listing_html(finca_raiz_html_dom_only)

        message = str(exc_info.value)
        assert "address" in message
        assert "latitude" in message
        assert "longitude" in message

    def test_raises_for_a_page_that_is_not_a_listing(self):
        with pytest.raises(ScrapeError):
            finca_raiz.parse_listing_html("<html><body>nothing here</body></html>")

    def test_survives_malformed_next_data_json(self, finca_raiz_html):
        """A broken tier 1 must fall through, not blow up."""
        broken = finca_raiz._NEXT_DATA_PATTERN.sub(
            '<script id="__NEXT_DATA__">{not json</script>', finca_raiz_html
        )

        result = finca_raiz.parse_listing_html(broken)

        assert result["purchase_price_cop"] == 700000000
        assert result["amenities"] == []


class TestParseListingHtmlStatus:
    def test_hidden_price_is_flagged_and_price_left_unset(
        self, finca_raiz_html, override_next_data
    ):
        """
        ``purchase_price_cop`` was made nullable precisely for this case - a
        listing with a hidden price is recorded, but without a fabricated price.
        """
        html = override_next_data(finca_raiz_html, hidePrice=True)

        result = finca_raiz.parse_listing_html(html)

        assert result["status"] == "price_hidden"
        assert result.get("purchase_price_cop") is None

    def test_sold_listing_is_flagged(self, finca_raiz_html, override_next_data):
        html = override_next_data(finca_raiz_html, sold=True)

        assert finca_raiz.parse_listing_html(html)["status"] == "sold"

    def test_inactive_listing_is_flagged(self, finca_raiz_html, override_next_data):
        html = override_next_data(finca_raiz_html, active=False)

        assert finca_raiz.parse_listing_html(html)["status"] == "inactive"

    def test_hidden_price_takes_precedence_over_sold(
        self, finca_raiz_html, override_next_data
    ):
        html = override_next_data(
            finca_raiz_html, hidePrice=True, sold=True, active=False
        )

        assert finca_raiz.parse_listing_html(html)["status"] == "price_hidden"

    def test_facilities_not_applicable_yields_no_amenities(
        self, finca_raiz_html, override_next_data
    ):
        html = override_next_data(finca_raiz_html, facilitiesNotApply=True)

        assert finca_raiz.parse_listing_html(html)["amenities"] == []


class TestFetch:
    def test_returns_page_body(self, http_requests_mock):
        http_requests_mock.get(LISTING_URL, text="<html>ok</html>")

        assert finca_raiz.fetch(LISTING_URL) == "<html>ok</html>"

    def test_sends_a_browser_user_agent(self, http_requests_mock):
        http_requests_mock.get(LISTING_URL, text="<html>ok</html>")

        finca_raiz.fetch(LISTING_URL)

        assert "Mozilla/5.0" in http_requests_mock.last_request.headers["User-Agent"]

    def test_raises_fetch_error_on_http_error(self, http_requests_mock):
        http_requests_mock.get(LISTING_URL, status_code=403)

        with pytest.raises(FetchError):
            finca_raiz.fetch(LISTING_URL)

    def test_raises_fetch_error_on_connection_failure(self, http_requests_mock):
        http_requests_mock.get(LISTING_URL, exc=requests.ConnectionError("boom"))

        with pytest.raises(FetchError):
            finca_raiz.fetch(LISTING_URL)
