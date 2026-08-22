from __future__ import annotations

import pytest
import requests
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from _factories.exchange_rate.db import ExchangeRateDBFactory
from _factories.listing.db import ListingDBFactory
from _factories.market.db import MarketDBFactory
from models.property.db import PropertyDB
from services.exchange_rate import FRANKFURTER_RATES_URL

LISTING_URL = (
    "https://www.fincaraiz.com.co/casa-en-venta-en-ahitamara-salento/193301244"
)

COP_PER_USD = 4150.0

MANUAL_BODY = {
    "source_url": "https://example.com/off-market/salento-finca",
    "address": "Vereda Boquia, Salento",
    "bedrooms": 3,
    "city": "Salento",
    "country": "Colombia",
    "latitude": 4.6381,
    "longitude": -75.5706,
    "neighborhood": "Boquia",
    "property_type": "Finca",
    "state": "Quindio",
}


@pytest.fixture
def stored_exchange_rate(mock_utcnow, test_db_session: Session):
    exchange_rate = ExchangeRateDBFactory(
        record_date=mock_utcnow.date(), cop_per_usd=COP_PER_USD
    )
    test_db_session.commit()
    return exchange_rate


@pytest.fixture
def finca_raiz_listing(http_requests_mock, finca_raiz_html):
    http_requests_mock.get(LISTING_URL, text=finca_raiz_html)
    return http_requests_mock


class TestCreatePropertyFromUrl:
    def test_scrapes_and_stores_the_listing(
        self, test_app_client, finca_raiz_listing, stored_exchange_rate
    ):
        result = test_app_client.post(
            "/api/properties", json={"source_url": LISTING_URL}
        )

        assert result.status_code == 201

        data = result.json()["data"]
        assert data["address"] == "CASA 1 MZ B/AHITAMARA/EL LIMONAR"
        assert data["amenities"] == ["Patio", "Servicios Públicos"]
        assert data["bedrooms"] == 5
        assert data["city"] == "Salento"
        assert data["country"] == "Colombia"
        assert data["name"] == "Casa en Venta en Ahitamara, Salento"
        assert data["neighborhood"] == "Ahitamara"
        assert data["property_type"] == "Casa"
        assert data["purchase_price_cop"] == 700000000
        assert data["source_url"] == LISTING_URL
        assert data["state"] == "Quindio"
        assert data["status"] == "active"

    def test_converts_price_with_our_own_rate_not_the_sites(
        self, test_app_client, finca_raiz_listing, stored_exchange_rate
    ):
        """
        Finca Raiz publishes 217599 USD for this listing off a ~3216 COP/USD rate.
        The stored figure has to come from our rate instead.
        """
        result = test_app_client.post(
            "/api/properties", json={"source_url": LISTING_URL}
        )

        purchase_price_usd = result.json()["data"]["purchase_price_usd"]

        assert purchase_price_usd == pytest.approx(700000000 / COP_PER_USD, rel=1e-6)
        assert purchase_price_usd != pytest.approx(217599, rel=1e-3)

    def test_resubmitting_the_same_url_updates_in_place(
        self, test_app_client, finca_raiz_listing, stored_exchange_rate, test_db_session
    ):
        first = test_app_client.post(
            "/api/properties", json={"source_url": LISTING_URL}
        )
        second = test_app_client.post(
            "/api/properties", json={"source_url": LISTING_URL}
        )

        assert first.status_code == 201
        assert second.status_code == 201
        assert first.json()["data"]["id"] == second.json()["data"]["id"]

        row_count = test_db_session.execute(
            select(func.count())
            .select_from(PropertyDB)
            .where(PropertyDB.source_url == LISTING_URL)
        ).scalar_one()
        assert row_count == 1

    def test_stores_without_a_usd_price_when_no_rate_can_be_resolved(
        self, test_app_client, finca_raiz_listing, http_requests_mock
    ):
        """No stored rate and frankfurter unreachable - the COP price is still worth keeping."""
        http_requests_mock.get(FRANKFURTER_RATES_URL, status_code=503)

        result = test_app_client.post(
            "/api/properties", json={"source_url": LISTING_URL}
        )

        assert result.status_code == 201
        assert result.json()["data"]["purchase_price_cop"] == 700000000
        assert result.json()["data"]["purchase_price_usd"] is None

    def test_fetches_a_rate_on_a_cold_database(
        self, test_app_client, finca_raiz_listing, http_requests_mock, mock_utcnow
    ):
        http_requests_mock.get(
            FRANKFURTER_RATES_URL,
            json=[
                {
                    "base": "USD",
                    "quote": "COP",
                    "date": str(mock_utcnow.date()),
                    "rate": COP_PER_USD,
                }
            ],
        )

        result = test_app_client.post(
            "/api/properties", json={"source_url": LISTING_URL}
        )

        assert result.status_code == 201
        assert result.json()["data"]["purchase_price_usd"] == pytest.approx(
            700000000 / COP_PER_USD, rel=1e-6
        )


class TestCreatePropertyErrors:
    def test_returns_400_for_an_unsupported_host(
        self, test_app_client, http_requests_mock
    ):
        result = test_app_client.post(
            "/api/properties",
            json={"source_url": "https://www.metrocuadrado.com/casa/1"},
        )

        assert result.status_code == 400
        assert "metrocuadrado.com" in result.json()["detail"]
        assert http_requests_mock.call_count == 0

    def test_returns_502_when_the_listing_page_cannot_be_reached(
        self, test_app_client, http_requests_mock
    ):
        http_requests_mock.get(LISTING_URL, exc=requests.ConnectionError("boom"))

        result = test_app_client.post(
            "/api/properties", json={"source_url": LISTING_URL}
        )

        assert result.status_code == 502

    def test_returns_502_on_an_http_error_from_the_listing_site(
        self, test_app_client, http_requests_mock
    ):
        http_requests_mock.get(LISTING_URL, status_code=403)

        result = test_app_client.post(
            "/api/properties", json={"source_url": LISTING_URL}
        )

        assert result.status_code == 502

    def test_returns_422_when_the_page_cannot_be_parsed(
        self, test_app_client, http_requests_mock
    ):
        http_requests_mock.get(LISTING_URL, text="<html><body>nope</body></html>")

        result = test_app_client.post(
            "/api/properties", json={"source_url": LISTING_URL}
        )

        assert result.status_code == 422

    def test_returns_422_without_a_source_url(self, test_app_client):
        result = test_app_client.post("/api/properties", json={})

        assert result.status_code == 422


class TestCreatePropertyManualEntry:
    def test_stores_the_body_without_fetching_anything(
        self, test_app_client, http_requests_mock, stored_exchange_rate
    ):
        result = test_app_client.post(
            "/api/properties",
            json={**MANUAL_BODY, "purchase_price_cop": 480000000},
        )

        assert result.status_code == 201
        assert http_requests_mock.call_count == 0

        data = result.json()["data"]
        assert data["address"] == MANUAL_BODY["address"]
        assert data["city"] == "Salento"
        assert data["purchase_price_cop"] == 480000000
        assert data["purchase_price_usd"] == pytest.approx(
            480000000 / COP_PER_USD, rel=1e-6
        )
        assert data["status"] == "active"

    def test_works_for_a_host_with_no_parser(
        self, test_app_client, http_requests_mock, stored_exchange_rate
    ):
        """A full manual body bypasses the parser registry entirely."""
        result = test_app_client.post(
            "/api/properties",
            json={**MANUAL_BODY, "source_url": "https://www.metrocuadrado.com/casa/1"},
        )

        assert result.status_code == 201
        assert http_requests_mock.call_count == 0

    def test_rejects_a_partial_manual_body(self, test_app_client, http_requests_mock):
        partial = {key: value for key, value in MANUAL_BODY.items() if key != "state"}

        result = test_app_client.post("/api/properties", json=partial)

        assert result.status_code == 422
        assert "state" in str(result.json())
        assert http_requests_mock.call_count == 0

    def test_rejects_manual_only_fields_on_the_scrape_path(
        self, test_app_client, http_requests_mock
    ):
        """
        Correcting a scraped price means sending a full manual body - a lone
        override would silently disagree with the rest of the scraped record.
        """
        result = test_app_client.post(
            "/api/properties",
            json={"source_url": LISTING_URL, "purchase_price_cop": 1},
        )

        assert result.status_code == 422
        assert "purchase_price_cop" in str(result.json())
        assert http_requests_mock.call_count == 0


class TestCreatePropertyOverrides:
    def test_supplied_name_beats_the_scraped_title(
        self, test_app_client, finca_raiz_listing, stored_exchange_rate
    ):
        result = test_app_client.post(
            "/api/properties",
            json={"source_url": LISTING_URL, "name": "Salento finca #2"},
        )

        assert result.status_code == 201
        assert result.json()["data"]["name"] == "Salento finca #2"

    def test_explicit_empty_amenities_clears_the_scraped_list(
        self, test_app_client, finca_raiz_listing, stored_exchange_rate
    ):
        """
        Checked with ``is not None`` rather than truthiness, so an explicit ``[]``
        clears rather than falling through to the scraped values.
        """
        result = test_app_client.post(
            "/api/properties",
            json={"source_url": LISTING_URL, "amenities": []},
        )

        assert result.status_code == 201
        assert result.json()["data"]["amenities"] == []

    def test_overrides_are_not_treated_as_a_partial_manual_body(
        self, test_app_client, finca_raiz_listing, stored_exchange_rate
    ):
        result = test_app_client.post(
            "/api/properties",
            json={
                "source_url": LISTING_URL,
                "description": "Needs a new roof",
                "name": "Salento finca #2",
                "notes": "Seen 2026-08-14",
            },
        )

        assert result.status_code == 201
        assert result.json()["data"]["description"] == "Needs a new roof"
        assert result.json()["data"]["notes"] == "Seen 2026-08-14"


# The Salento centroid the ingested listings below average out to. The fixture
# listing page sits 10.8km from it and ``MANUAL_BODY`` all but on top of it.
SALENTO_CENTROID = (4.6375, -75.5703)

# Roughly 640km away, so nothing on the roster is within the match radius.
CARTAGENA = (10.3910, -75.4794)


class TestCreatePropertyMarketResolution:
    """
    ``properties.market_id`` is the join key the budget indicator needs.
    ``properties.city`` cannot be it: Finca Raiz files a Pance cabin under
    ``city='Cali'`` while ``markets.locality`` is AirROI's ``'Pance'``.
    """

    @pytest.fixture
    def salento_market(self, test_db_session):
        latitude, longitude = SALENTO_CENTROID
        market = MarketDBFactory(
            country="Colombia", region="Quindío", locality="Salento", district=None
        )
        # Committed before the listing: ``listings.market_id`` is a real foreign
        # key and the factories pass it as a plain value, so nothing tells the
        # unit of work to insert the market first.
        test_db_session.commit()

        ListingDBFactory(
            market_id=market.id,
            latitude=latitude,
            longitude=longitude,
            location=f"POINT({longitude} {latitude})",
        )
        test_db_session.commit()
        return market

    def test_files_a_scraped_property_under_its_market(
        self,
        test_app_client,
        finca_raiz_listing,
        salento_market,
        stored_exchange_rate,
    ):
        result = test_app_client.post(
            "/api/properties", json={"source_url": LISTING_URL}
        )

        assert result.status_code == 201
        assert result.json()["data"]["market_id"] == str(salento_market.id)

    def test_files_a_manual_property_under_its_market(
        self, test_app_client, salento_market, stored_exchange_rate
    ):
        result = test_app_client.post("/api/properties", json=MANUAL_BODY)

        assert result.status_code == 201
        assert result.json()["data"]["market_id"] == str(salento_market.id)

    def test_stores_no_market_for_a_property_outside_every_market(
        self, test_app_client, salento_market, stored_exchange_rate
    ):
        latitude, longitude = CARTAGENA
        body = {**MANUAL_BODY, "latitude": latitude, "longitude": longitude}

        result = test_app_client.post("/api/properties", json=body)

        # Still a 201: an unmatched property is worth storing, it just cannot
        # contribute to any market's budget indicator.
        assert result.status_code == 201
        assert result.json()["data"]["market_id"] is None

    def test_stores_no_market_when_nothing_has_been_ingested(
        self, test_app_client, stored_exchange_rate, test_db_session
    ):
        MarketDBFactory(
            country="Colombia", region="Quindío", locality="Salento", district=None
        )
        test_db_session.commit()

        result = test_app_client.post("/api/properties", json=MANUAL_BODY)

        # The market exists but has no listings, so it has no centroid and there
        # is nothing to measure the property against.
        assert result.status_code == 201
        assert result.json()["data"]["market_id"] is None
