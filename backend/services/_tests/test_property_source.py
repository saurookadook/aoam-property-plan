from __future__ import annotations

import pytest

from services import property_source
from services.exceptions import UnsupportedSource

LISTING_URL = (
    "https://www.fincaraiz.com.co/casa-en-venta-en-ahitamara-salento/193301244"
)


class TestResolveHost:
    @pytest.mark.parametrize(
        "url, expected",
        [
            ("https://www.fincaraiz.com.co/casa/1", "fincaraiz.com.co"),
            ("https://fincaraiz.com.co/casa/1", "fincaraiz.com.co"),
            ("http://WWW.FincaRaiz.com.co/casa/1", "fincaraiz.com.co"),
            ("https://fincaraiz.com.co:443/casa/1", "fincaraiz.com.co"),
            ("https://www.metrocuadrado.com/casa/1", "metrocuadrado.com"),
            ("not-a-url", ""),
        ],
    )
    def test_normalises_host(self, url, expected):
        assert property_source.resolve_host(url) == expected


class TestParse:
    def test_dispatches_to_the_finca_raiz_parser(self, finca_raiz_html):
        result = property_source.parse(LISTING_URL, finca_raiz_html)

        assert result["city"] == "Salento"
        assert result["purchase_price_cop"] == 700000000

    def test_raises_for_an_unregistered_host(self, finca_raiz_html):
        with pytest.raises(UnsupportedSource) as exc_info:
            property_source.parse(
                "https://www.metrocuadrado.com/casa/1", finca_raiz_html
            )

        assert "metrocuadrado.com" in str(exc_info.value)

    def test_error_names_the_supported_hosts(self, finca_raiz_html):
        with pytest.raises(UnsupportedSource) as exc_info:
            property_source.parse("https://example.com/casa/1", finca_raiz_html)

        assert "fincaraiz.com.co" in str(exc_info.value)


class TestScrape:
    def test_fetches_parses_and_records_the_source_url(
        self, http_requests_mock, finca_raiz_html
    ):
        http_requests_mock.get(LISTING_URL, text=finca_raiz_html)

        result = property_source.scrape(LISTING_URL)

        assert result["source_url"] == LISTING_URL
        assert result["city"] == "Salento"
        assert result["amenities"] == ["Patio", "Servicios Públicos"]

    def test_does_not_fetch_an_unsupported_host(self, http_requests_mock):
        """The host is rejected before any network call is made."""
        with pytest.raises(UnsupportedSource):
            property_source.scrape("https://www.metrocuadrado.com/casa/1")

        assert http_requests_mock.call_count == 0
