from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from _factories.exchange_rate.db import ExchangeRateDBFactory
from _factories.property.db import PropertyDBFactory
from constants import AIRROI_BASE_URL

COP_PER_USD = 4150.0

COMPARABLES_URL = f"{AIRROI_BASE_URL}/listings/comparables"
ESTIMATE_URL = f"{AIRROI_BASE_URL}/calculator/estimate"

CALIMA = (3.9251, -76.6265)
SALENTO = (4.6375, -75.5703)

UNKNOWN_ID = "988d0b5d-d4a5-4808-a94d-2d9df1df7588"


@pytest.fixture(autouse=True)
def stored_exchange_rate(mock_utcnow, test_db_session: Session):
    ExchangeRateDBFactory(record_date=mock_utcnow.date(), cop_per_usd=COP_PER_USD)
    test_db_session.commit()


@pytest.fixture
def salento_property(test_db_session: Session):
    latitude, longitude = SALENTO
    property_record = PropertyDBFactory(
        latitude=latitude,
        longitude=longitude,
        baths=2.0,
        bedrooms=3,
        guests=8,
        notes=None,
        purchase_price_cop=500_000_000.0,
        source_url="https://example.com/property/salento",
    )
    test_db_session.commit()
    return property_record


class TestAnalyzeProperty:
    def test_an_empty_body_analyses_on_the_colombia_defaults(
        self, airroi_estimate_mock, salento_property, test_app_client
    ):
        result = test_app_client.post(f"/api/properties/{salento_property.id}/analyze")

        assert result.status_code == 201
        data = result.json()["data"]
        assert data["annual_revenue_source"] == "airroi_p25"
        assert data["comp_count"] == 17
        assert data["peak_months"] == ["December", "July", "January"]
        assert data["down_payment_percentage"] == pytest.approx(30.0)
        assert data["interest_rate"] == pytest.approx(10.0)
        assert data["exchange_rate"] == pytest.approx(COP_PER_USD)

    def test_overrides_are_applied(
        self, airroi_estimate_mock, salento_property, test_app_client
    ):
        result = test_app_client.post(
            f"/api/properties/{salento_property.id}/analyze",
            json={
                "down_payment_percentage": 40,
                "interest_rate_percentage": 8,
                "hoa_monthly_cop": 0,
            },
        )

        assert result.status_code == 201
        data = result.json()["data"]
        assert data["down_payment_percentage"] == pytest.approx(40.0)
        assert data["interest_rate"] == pytest.approx(8.0)
        # An explicit ``0`` is a choice, not an omission.
        assert data["hoa_monthly_cop"] == pytest.approx(0.0)

    @pytest.mark.parametrize(
        "body",
        [
            {"down_payment_percentage": 140},
            {"interest_rate_percentage": -1},
            {"loan_term_years": 0},
            {"purchase_price_cop": 0},
        ],
    )
    def test_out_of_bounds_assumptions_are_rejected_before_any_api_call(
        self, airroi_estimate_mock, body, salento_property, test_app_client
    ):
        # The request model is generated from ``PropertyScenario`` and keeps its
        # bounds, so this fails at the edge rather than inside ``analyze()``.
        result = test_app_client.post(
            f"/api/properties/{salento_property.id}/analyze", json=body
        )

        assert result.status_code == 422
        assert airroi_estimate_mock.call_count == 0

    def test_every_call_writes_a_new_report(
        self, airroi_estimate_mock, salento_property, test_app_client
    ):
        first = test_app_client.post(f"/api/properties/{salento_property.id}/analyze")
        second = test_app_client.post(
            f"/api/properties/{salento_property.id}/analyze",
            json={"down_payment_percentage": 50},
        )

        assert first.json()["data"]["id"] != second.json()["data"]["id"]

    def test_an_unknown_property_is_404(self, airroi_estimate_mock, test_app_client):
        result = test_app_client.post(f"/api/properties/{UNKNOWN_ID}/analyze")

        assert result.status_code == 404
        assert result.json()["detail"] == "Property not found"

    def test_a_property_with_no_bath_count_is_422(
        self, airroi_estimate_mock, test_app_client, test_db_session
    ):
        property_record = PropertyDBFactory(
            baths=None,
            bedrooms=3,
            guests=None,
            notes="Seen 2026-08-14",
            purchase_price_cop=500_000_000.0,
            source_url="https://example.com/property/no-baths",
        )
        test_db_session.commit()

        result = test_app_client.post(f"/api/properties/{property_record.id}/analyze")

        assert result.status_code == 422
        assert "bath count" in result.json()["detail"]

    def test_a_hidden_price_is_422_until_one_is_supplied(
        self, airroi_estimate_mock, test_app_client, test_db_session
    ):
        latitude, longitude = SALENTO
        property_record = PropertyDBFactory(
            latitude=latitude,
            longitude=longitude,
            baths=2.0,
            bedrooms=3,
            guests=8,
            notes=None,
            purchase_price_cop=None,
            status="price_hidden",
            source_url="https://example.com/property/price-hidden",
        )
        test_db_session.commit()

        refused = test_app_client.post(f"/api/properties/{property_record.id}/analyze")
        assert refused.status_code == 422
        assert "purchase price" in refused.json()["detail"]

        accepted = test_app_client.post(
            f"/api/properties/{property_record.id}/analyze",
            json={"purchase_price_cop": 700_000_000.0},
        )
        assert accepted.status_code == 201
        assert accepted.json()["data"]["purchase_price_cop"] == pytest.approx(
            700_000_000.0
        )

    def test_an_airroi_failure_is_502_not_500(
        self, http_requests_mock, salento_property, test_app_client
    ):
        # Our side worked; an upstream we depend on did not.
        http_requests_mock.get(ESTIMATE_URL, status_code=500, json={})

        result = test_app_client.post(f"/api/properties/{salento_property.id}/analyze")

        assert result.status_code == 502
        assert result.json()["detail"] == (
            "Could not retrieve revenue data from AirROI"
        )

    def test_a_thin_comp_set_still_returns_a_report(
        self,
        airroi_estimate_mock,
        http_requests_mock,
        test_app_client,
        test_db_session,
    ):
        latitude, longitude = CALIMA
        property_record = PropertyDBFactory(
            latitude=latitude,
            longitude=longitude,
            baths=2.0,
            bedrooms=2,
            guests=4,
            notes=None,
            purchase_price_cop=400_000_000.0,
            source_url="https://example.com/property/calima",
        )
        test_db_session.commit()
        http_requests_mock.get(COMPARABLES_URL, json={"results": []})

        result = test_app_client.post(f"/api/properties/{property_record.id}/analyze")

        assert result.status_code == 201
        data = result.json()["data"]
        assert data["comp_derived_revenue_cop"] is None
        assert data["annual_revenue_source"] == "airroi_p25_thin_comps"


class TestReadPropertyComps:
    def test_refreshes_from_airroi_on_every_call(
        self, airroi_estimate_mock, salento_property, test_app_client
    ):
        result = test_app_client.get(f"/api/properties/{salento_property.id}/comps")

        assert result.status_code == 200
        assert airroi_estimate_mock.call_count == 1

        comps = result.json()["data"]
        assert len(comps) == 25
        assert all(comp["distance_km"] is not None for comp in comps)
        assert comps[0]["distance_km"] <= comps[-1]["distance_km"]

    def test_an_unknown_property_is_404(self, airroi_estimate_mock, test_app_client):
        result = test_app_client.get(f"/api/properties/{UNKNOWN_ID}/comps")

        assert result.status_code == 404

    def test_an_airroi_failure_is_502(
        self, http_requests_mock, salento_property, test_app_client
    ):
        http_requests_mock.get(ESTIMATE_URL, status_code=500, json={})

        result = test_app_client.get(f"/api/properties/{salento_property.id}/comps")

        assert result.status_code == 502


class TestReadCachedPropertyComps:
    def test_makes_no_airroi_call(
        self, airroi_estimate_mock, salento_property, test_app_client
    ):
        test_app_client.post(f"/api/properties/{salento_property.id}/analyze")
        calls_after_analysis = airroi_estimate_mock.call_count

        result = test_app_client.get(
            f"/api/properties/{salento_property.id}/comps/cached"
        )

        assert result.status_code == 200
        assert airroi_estimate_mock.call_count == calls_after_analysis
        assert len(result.json()["data"]) == 25

    def test_returns_the_same_comps_the_analysis_was_built_on(
        self, airroi_estimate_mock, salento_property, test_app_client
    ):
        live = test_app_client.get(f"/api/properties/{salento_property.id}/comps")
        cached = test_app_client.get(
            f"/api/properties/{salento_property.id}/comps/cached"
        )

        assert [comp["id"] for comp in cached.json()["data"]] == [
            comp["id"] for comp in live.json()["data"]
        ]

    def test_an_unanalysed_property_is_an_empty_list_not_a_404(
        self, airroi_estimate_mock, salento_property, test_app_client
    ):
        result = test_app_client.get(
            f"/api/properties/{salento_property.id}/comps/cached"
        )

        assert result.status_code == 200
        assert result.json()["data"] == []
        assert airroi_estimate_mock.call_count == 0

    def test_an_unknown_property_is_404(self, test_app_client):
        result = test_app_client.get(f"/api/properties/{UNKNOWN_ID}/comps/cached")

        assert result.status_code == 404
        assert result.json()["detail"] == "Property not found"
