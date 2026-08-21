from __future__ import annotations

import json

import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from _factories.exchange_rate.db import ExchangeRateDBFactory
from _factories.property.db import PropertyDBFactory
from constants import AIRROI_BASE_URL
from models.exchange_rate.db import ExchangeRateDB
from models.listing.db import ListingDB
from models.listing.facade import ListingFacade
from models.listing_financial_report.facade import ListingFinancialReportFacade
from models.property_comp.db import PropertyCompDB
from models.property_comp.facade import PropertyCompFacade
from models.property_financial_report.facade import PropertyFinancialReportFacade
from services import property_analysis
from services.exceptions import AirROIError
from services.exchange_rate import FRANKFURTER_RATES_URL
from services.property_analysis import analyze_property, refresh_comps

COP_PER_USD = 4150.0

COMPARABLES_URL = f"{AIRROI_BASE_URL}/listings/comparables"
ESTIMATE_URL = f"{AIRROI_BASE_URL}/calculator/estimate"

# Coordinates each capture was taken at - see ``airroi_estimate_captures``.
BOGOTA = (4.7110, -74.0721)
CALIMA = (3.9251, -76.6265)
SALENTO = (4.6375, -75.5703)


@pytest.fixture(autouse=True)
def stored_exchange_rate(mock_utcnow, test_db_session: Session):
    ExchangeRateDBFactory(record_date=mock_utcnow.date(), cop_per_usd=COP_PER_USD)
    test_db_session.commit()


@pytest.fixture
def build_property(test_db_session: Session):
    def _build(*, coordinates, bedrooms, **overrides):
        latitude, longitude = coordinates
        property_record = PropertyDBFactory(
            **{
                "baths": 2.0,
                "guests": 8,
                "notes": None,
                "purchase_price_cop": 500_000_000.0,
                **overrides,
                "bedrooms": bedrooms,
                "latitude": latitude,
                "longitude": longitude,
            }
        )
        test_db_session.commit()
        return property_record

    return _build


@pytest.fixture
def salento_3br(build_property):
    return build_property(coordinates=SALENTO, bedrooms=3, baths=2.0, guests=8)


class TestAnalyzePropertySalento:
    """
    The healthy path: 25 comps, a comp-derived estimate, and a contest between it
    and AirROI's own p25.
    """

    def test_persists_every_comp_with_a_distance_and_frozen_metrics(
        self, airroi_estimate_mock, salento_3br, test_db_session
    ):
        analyze_property(test_db_session, property_id=salento_3br.id)

        persisted = test_db_session.execute(
            select(func.count())
            .select_from(PropertyCompDB)
            .where(PropertyCompDB.property_id == salento_3br.id)
        ).scalar_one()
        assert persisted == 25

        comps = PropertyCompFacade(db_session=test_db_session).get_all_by_property_id(
            salento_3br.id
        )
        assert all(comp.distance_km is not None for comp in comps)
        assert all(comp.captured_at is not None for comp in comps)
        # Every Salento comp sits inside a kilometre of the property.
        assert comps[-1].distance_km < 1.0
        assert comps[0].distance_km <= comps[-1].distance_km

    def test_persists_the_comps_as_listings_and_financial_reports(
        self, airroi_estimate_mock, salento_3br, test_db_session
    ):
        analyze_property(test_db_session, property_id=salento_3br.id)

        listings = test_db_session.execute(select(ListingDB)).scalars().all()
        assert len(listings) == 25
        # A comp arrives from a coordinate lookup, not from one of our markets.
        assert all(listing.market_id is None for listing in listings)

        first_comp = ListingFacade(db_session=test_db_session).get_one_by_airroi_id(
            1116177604790567078
        )
        reports = ListingFinancialReportFacade(
            db_session=test_db_session
        ).get_all_by_listing_id(first_comp.id)

        assert len(reports) == 1
        # AirROI calls these ``num_reviews`` and ``ttm_occupancy``.
        assert reports[0].number_of_reviews == 99
        assert reports[0].ttm_occupancy_rate == pytest.approx(0.345)
        assert reports[0].ttm_revenue == pytest.approx(36564000.0)

    def test_records_the_airroi_percentiles_and_seasonality(
        self, airroi_estimate_mock, salento_3br, test_db_session
    ):
        report = analyze_property(test_db_session, property_id=salento_3br.id)

        assert report.airroi_revenue_p25_cop == pytest.approx(36074113.00115585)
        assert report.airroi_revenue_p50_cop == pytest.approx(46449197.47648239)
        assert report.airroi_revenue_p90_cop == pytest.approx(101136089.92168903)
        # ``revenue`` is the mean, not a typical outcome - stored for reference,
        # never analysed against.
        assert report.airroi_revenue_cop == pytest.approx(52217691.63147078)
        assert report.airroi_adr_cop == pytest.approx(349873.6973140861)
        assert report.airroi_occupancy_rate == pytest.approx(0.4230864774592918)

        assert report.peak_months == ["December", "July", "January"]
        assert len(report.monthly_revenue_distribution or []) == 12
        assert sum(report.monthly_revenue_distribution or []) == pytest.approx(
            1.0, abs=1e-5
        )

    def test_comp_derived_estimate_is_the_median_of_the_surviving_comps(
        self, airroi_estimate_mock, salento_3br, test_db_session
    ):
        report = analyze_property(test_db_session, property_id=salento_3br.id)

        # 17 of the 25 comps reconcile. NOTE: the plan's 40,427,441 is the median
        # over all 25 - and is itself the projection of a comp the gate drops, at
        # a 23% gap. Gating is the specified behaviour, so this is the figure.
        assert report.comp_count == 17
        assert report.comp_derived_revenue_cop == pytest.approx(51274712, rel=1e-6)

    def test_the_conservative_estimate_wins_and_is_named(
        self, airroi_estimate_mock, salento_3br, test_db_session
    ):
        report = analyze_property(test_db_session, property_id=salento_3br.id)

        # p25 (36.1M) is below the comp-derived median (51.3M) here. Which one
        # wins flips by market, which is why the source is stored at all.
        assert report.annual_revenue_source == "airroi_p25"
        assert report.annual_revenue_cop == pytest.approx(36074113.00115585)

    def test_usd_mirrors_use_our_own_rate(
        self, airroi_estimate_mock, salento_3br, test_db_session
    ):
        report = analyze_property(test_db_session, property_id=salento_3br.id)

        assert report.exchange_rate == pytest.approx(COP_PER_USD)
        assert report.annual_revenue_usd == pytest.approx(
            (report.annual_revenue_cop or 0.0) / COP_PER_USD
        )
        assert report.annual_net_income_usd == pytest.approx(
            (report.annual_net_income_cop or 0.0) / COP_PER_USD
        )

    def test_stamps_calculated_at_and_the_inputs_it_ran_against(
        self, airroi_estimate_mock, mock_utcnow, salento_3br, test_db_session
    ):
        report = analyze_property(test_db_session, property_id=salento_3br.id)

        # Stamped by the persistence layer, not inside ``analyze()``, and
        # timezone-aware - the column was missed by ``fd50b58f027e``.
        assert report.calculated_at is not None
        assert report.calculated_at.tzinfo is not None
        assert report.calculated_at > mock_utcnow
        # The scenario's own knobs are stored so the row explains itself later.
        assert report.purchase_price_cop == pytest.approx(500_000_000.0)
        assert report.down_payment_percentage == pytest.approx(30.0)
        assert report.interest_rate == pytest.approx(10.0)
        assert report.management_fee_percentage == pytest.approx(22.0)
        assert report.predial_rate_percentage == pytest.approx(0.8)
        assert report.monthly_mortgage_cop is not None

    def test_re_analysing_updates_the_comps_rather_than_duplicating_them(
        self, airroi_estimate_mock, salento_3br, test_db_session
    ):
        analyze_property(test_db_session, property_id=salento_3br.id)
        analyze_property(test_db_session, property_id=salento_3br.id)

        persisted = test_db_session.execute(
            select(func.count())
            .select_from(PropertyCompDB)
            .where(PropertyCompDB.property_id == salento_3br.id)
        ).scalar_one()

        assert persisted == 25


class TestThinCompSets:
    """
    Calima is the doc's top-ranked market and has one comparable listing. This is
    the case most likely to be "fixed" into a false positive.
    """

    @pytest.fixture
    def calima_2br(self, build_property):
        return build_property(coordinates=CALIMA, bedrooms=2, baths=2.0, guests=4)

    def test_a_single_comp_yields_no_comp_derived_estimate(
        self, airroi_estimate_mock, http_requests_mock, calima_2br, test_db_session
    ):
        http_requests_mock.get(COMPARABLES_URL, json={"results": []})

        report = analyze_property(test_db_session, property_id=calima_2br.id)

        assert report.comp_derived_revenue_cop is None
        assert report.comp_count == 0

    def test_the_report_still_persists_off_p25_and_says_why(
        self, airroi_estimate_mock, http_requests_mock, calima_2br, test_db_session
    ):
        http_requests_mock.get(COMPARABLES_URL, json={"results": []})

        report = analyze_property(test_db_session, property_id=calima_2br.id)

        assert report.id is not None
        assert report.annual_revenue_source == "airroi_p25_thin_comps"
        assert report.annual_revenue_cop == pytest.approx(19723627, rel=1e-6)
        assert report.annual_revenue_cop == pytest.approx(report.airroi_revenue_p25_cop)

    def test_a_thin_set_triggers_exactly_one_fallback_lookup(
        self, airroi_estimate_mock, http_requests_mock, calima_2br, test_db_session
    ):
        fallback = http_requests_mock.get(COMPARABLES_URL, json={"results": []})

        analyze_property(test_db_session, property_id=calima_2br.id)

        assert fallback.call_count == 1

    def test_a_healthy_set_never_reaches_the_fallback(
        self, airroi_estimate_mock, http_requests_mock, salento_3br, test_db_session
    ):
        fallback = http_requests_mock.get(COMPARABLES_URL, json={"results": []})

        analyze_property(test_db_session, property_id=salento_3br.id)

        assert fallback.call_count == 0

    def test_a_failing_fallback_does_not_lose_the_report(
        self, airroi_estimate_mock, http_requests_mock, calima_2br, test_db_session
    ):
        # Best-effort by design: the primary estimate already succeeded.
        http_requests_mock.get(COMPARABLES_URL, status_code=500, json={})

        report = analyze_property(test_db_session, property_id=calima_2br.id)

        assert report.annual_revenue_source == "airroi_p25_thin_comps"

    def test_fallback_comps_are_merged_and_counted(
        self,
        airroi_estimate_mock,
        airroi_estimate_captures,
        http_requests_mock,
        calima_2br,
        test_db_session,
    ):
        # ``/listings/comparables`` has no capture, and the two endpoints that do
        # disagree on the key, so the service accepts either.
        borrowed = airroi_estimate_captures[(*SALENTO, 3)]["comparable_listings"]
        http_requests_mock.get(COMPARABLES_URL, json={"results": borrowed})

        report = analyze_property(test_db_session, property_id=calima_2br.id)

        assert report.comp_count == 17
        assert report.comp_derived_revenue_cop is not None
        assert report.annual_revenue_source in ("airroi_p25", "comp_derived")


class TestPeakMonths:
    def test_top_three_answers_where_the_15_percent_rule_does_not(
        self,
        airroi_estimate_mock,
        airroi_estimate_captures,
        build_property,
        test_db_session,
    ):
        bogota_2br = build_property(coordinates=BOGOTA, bedrooms=2, baths=2.0, guests=4)
        distribution = airroi_estimate_captures[(*BOGOTA, 2)][
            "monthly_revenue_distributions"
        ]

        # The doc's rule: months more than 15% above the annual average. This is
        # the capture where it finds nothing at all.
        assert not [share for share in distribution if share > (1 / 12) * 1.15]

        report = analyze_property(test_db_session, property_id=bogota_2br.id)

        assert len(report.peak_months or []) == 3

    def test_ranks_by_share_and_breaks_ties_on_the_earlier_month(self):
        flat = [1 / 12] * 12

        assert property_analysis.peak_months(flat) == [
            "January",
            "February",
            "March",
        ]

    def test_returns_an_empty_list_without_a_distribution(self):
        assert property_analysis.peak_months([]) == []


class TestCompReconciliationGate:
    def _comp(self, **metrics):
        return {
            "listing_info": {"listing_id": 42},
            "performance_metrics": {
                "ttm_avg_rate": 400_000.0,
                "ttm_occupancy": 0.5,
                "ttm_total_days": 365,
                "ttm_revenue": 73_000_000.0,
                **metrics,
            },
        }

    def _comp_with_gap(self, gap: float):
        """
        A comp whose reported revenue sits exactly ``gap`` away from its implied
        one - the gate divides by the *reported* figure, so that is the
        denominator the offset has to be built against.
        """
        implied = 400_000.0 * 0.5 * 365

        return self._comp(ttm_revenue=implied / (1 + gap))

    def test_a_reconciling_comp_projects_a_full_year(self):
        result = property_analysis._projected_revenue_cop(self._comp())

        assert result == pytest.approx(400_000.0 * 0.5 * 365)

    def test_a_part_year_listing_whose_figures_disagree_is_dropped_and_logged(
        self, caplog
    ):
        # 400,000 x 0.5 x 180 = 36,000,000 against a reported 10,000,000.
        comp = self._comp(ttm_total_days=180, ttm_revenue=10_000_000.0)

        with caplog.at_level("INFO", logger=property_analysis.__name__):
            assert property_analysis._projected_revenue_cop(comp) is None

        assert "does not reconcile" in caplog.text
        assert "42" in caplog.text

    def test_ttm_total_days_is_a_gate_not_a_multiplier(self):
        # Half a year live, and the reported revenue agrees with it. The comp
        # survives, and its projection is still a full 365 days.
        comp = self._comp(ttm_total_days=180, ttm_revenue=400_000.0 * 0.5 * 180)

        assert property_analysis._projected_revenue_cop(comp) == pytest.approx(
            400_000.0 * 0.5 * 365
        )

    @pytest.mark.parametrize("gap", [0.0, 0.05, 0.099])
    def test_gaps_inside_the_tolerance_survive(self, gap):
        assert (
            property_analysis._projected_revenue_cop(self._comp_with_gap(gap))
            is not None
        )

    @pytest.mark.parametrize("gap", [0.101, 0.5, 2.0])
    def test_gaps_outside_the_tolerance_are_dropped(self, gap):
        assert (
            property_analysis._projected_revenue_cop(self._comp_with_gap(gap)) is None
        )

    @pytest.mark.parametrize(
        "metrics",
        [
            {"ttm_avg_rate": None},
            {"ttm_occupancy": None},
            {"ttm_revenue": None},
            {"ttm_total_days": 0},
        ],
    )
    def test_comps_that_cannot_be_checked_are_excluded(self, metrics):
        assert property_analysis._projected_revenue_cop(self._comp(**metrics)) is None


class TestResolvingMissingInputs:
    def test_baths_fall_back_to_the_notes_json(
        self, airroi_estimate_mock, build_property, test_db_session
    ):
        property_record = build_property(
            coordinates=SALENTO,
            bedrooms=3,
            baths=None,
            guests=8,
            notes=json.dumps({"bathrooms": 2, "m2": 80}),
        )

        analyze_property(test_db_session, property_id=property_record.id)

        assert airroi_estimate_mock.last_request.qs["baths"] == ["2.0"]

    def test_guests_fall_back_to_two_per_bedroom(
        self, airroi_estimate_mock, build_property, test_db_session
    ):
        property_record = build_property(
            coordinates=SALENTO, bedrooms=3, baths=2.0, guests=None
        )

        analyze_property(test_db_session, property_id=property_record.id)

        # Deliberately conservative: the captured median is 8 for a 3-bedroom,
        # so this biases the comp set toward smaller units.
        assert airroi_estimate_mock.last_request.qs["guests"] == ["6"]

    def test_free_text_notes_do_not_yield_a_bath_count(
        self, airroi_estimate_mock, build_property, test_db_session
    ):
        # ``notes`` is free text and the properties route accepts a sentence.
        property_record = build_property(
            coordinates=SALENTO, bedrooms=3, baths=None, notes="Seen 2026-08-14"
        )

        with pytest.raises(ValueError, match="bath count"):
            analyze_property(test_db_session, property_id=property_record.id)

        assert airroi_estimate_mock.call_count == 0

    def test_a_hidden_price_can_be_supplied_with_the_request(
        self, airroi_estimate_mock, build_property, test_db_session
    ):
        property_record = build_property(
            coordinates=SALENTO, bedrooms=3, purchase_price_cop=None
        )

        with pytest.raises(ValueError, match="purchase price"):
            analyze_property(test_db_session, property_id=property_record.id)

        report = analyze_property(
            test_db_session,
            property_id=property_record.id,
            overrides={"purchase_price_cop": 700_000_000.0},
        )

        assert report.purchase_price_cop == pytest.approx(700_000_000.0)

    def test_no_exchange_rate_stops_the_analysis(
        self, airroi_estimate_mock, http_requests_mock, salento_3br, test_db_session
    ):
        test_db_session.execute(delete(ExchangeRateDB))
        # The cold-start fetch is the only other source, and it fails here.
        http_requests_mock.get(FRANKFURTER_RATES_URL, status_code=500, json={})

        with pytest.raises(ValueError, match="exchange rate"):
            analyze_property(test_db_session, property_id=salento_3br.id)


class TestOverrides:
    def test_scenario_knobs_reach_the_stored_report(
        self, airroi_estimate_mock, salento_3br, test_db_session
    ):
        report = analyze_property(
            test_db_session,
            property_id=salento_3br.id,
            overrides={
                "down_payment_percentage": 40.0,
                "interest_rate_percentage": 8.0,
                "hoa_monthly_cop": 0.0,
                "renovation_budget_cop": 25_000_000.0,
            },
        )

        assert report.down_payment_percentage == pytest.approx(40.0)
        assert report.interest_rate == pytest.approx(8.0)
        # ``0`` is a real choice, not an absent one.
        assert report.hoa_monthly_cop == pytest.approx(0.0)
        assert report.renovation_budget_cop == pytest.approx(25_000_000.0)

    def test_the_derived_revenue_cannot_be_overridden(
        self, airroi_estimate_mock, salento_3br, test_db_session
    ):
        report = analyze_property(
            test_db_session,
            property_id=salento_3br.id,
            overrides={"annual_revenue_cop": 999_999_999.0},
        )

        assert report.annual_revenue_cop != pytest.approx(999_999_999.0)


class TestUpstreamFailures:
    def test_an_airroi_failure_propagates(
        self, http_requests_mock, salento_3br, test_db_session
    ):
        http_requests_mock.get(ESTIMATE_URL, status_code=500, json={})

        with pytest.raises(AirROIError):
            analyze_property(test_db_session, property_id=salento_3br.id)

    def test_a_response_with_no_revenue_figure_is_an_airroi_error(
        self, http_requests_mock, salento_3br, test_db_session
    ):
        http_requests_mock.get(
            ESTIMATE_URL, json={"comparable_listings": [], "percentiles": {}}
        )
        http_requests_mock.get(COMPARABLES_URL, json={"results": []})

        with pytest.raises(AirROIError, match="no revenue figure"):
            analyze_property(test_db_session, property_id=salento_3br.id)

    def test_one_malformed_comp_does_not_lose_the_others(
        self,
        airroi_estimate_captures,
        http_requests_mock,
        salento_3br,
        test_db_session,
    ):
        capture = json.loads(json.dumps(airroi_estimate_captures[(*SALENTO, 3)]))
        # Each comp is written inside its own SAVEPOINT, so a broken one rolls
        # back alone rather than poisoning the request's transaction.
        del capture["comparable_listings"][0]["property_details"]["bedrooms"]
        http_requests_mock.get(ESTIMATE_URL, json=capture)

        report = analyze_property(test_db_session, property_id=salento_3br.id)

        persisted = test_db_session.execute(
            select(func.count())
            .select_from(PropertyCompDB)
            .where(PropertyCompDB.property_id == salento_3br.id)
        ).scalar_one()

        assert persisted == 24
        assert report.id is not None


class TestRefreshComps:
    def test_returns_the_stored_comps_nearest_first(
        self, airroi_estimate_mock, salento_3br, test_db_session
    ):
        comps = refresh_comps(test_db_session, property_id=salento_3br.id)

        assert len(comps) == 25
        assert airroi_estimate_mock.call_count == 1
        assert comps[0].distance_km <= comps[-1].distance_km

    def test_writes_no_financial_report(
        self, airroi_estimate_mock, salento_3br, test_db_session
    ):
        refresh_comps(test_db_session, property_id=salento_3br.id)

        assert (
            PropertyFinancialReportFacade(
                db_session=test_db_session
            ).get_latest_by_property_id(salento_3br.id)
            is None
        )

    def test_needs_no_purchase_price_or_exchange_rate(
        self, airroi_estimate_mock, build_property, test_db_session
    ):
        property_record = build_property(
            coordinates=SALENTO, bedrooms=3, purchase_price_cop=None
        )
        test_db_session.execute(delete(ExchangeRateDB))

        assert len(refresh_comps(test_db_session, property_id=property_record.id)) == 25
