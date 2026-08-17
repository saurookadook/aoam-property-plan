"""
Turns a stored property into a persisted financial report.

The one place that knows how an AirROI payload becomes rows. ``services.airroi``
fetches, ``services.calculations`` does arithmetic, ``services.geo`` measures, and
this module is the only thing that holds all three plus a database session.

Two revenue estimates are produced and both are kept. AirROI's own calculator
gives one; the median of ``adr x occupancy x 365`` over its comp set gives
another. Which is lower flips by market - in the captured data comps run about 2x
the direct estimate in Bogota and 0.77x in Salento - so neither can be assumed to
be the cautious one. ``conservative_of`` decides per property, and
``annual_revenue_source`` records the answer, because a stored revenue figure is
uninterpretable without it.

Nothing here commits. The route's session dependency owns the transaction; each
comp is written inside a ``SAVEPOINT`` so one malformed comparable rolls back
alone instead of taking the report with it.
"""

from __future__ import annotations

import json
import logging
import statistics
from datetime import datetime, timezone
from typing import Any, Optional, cast
from uuid import UUID

from sqlalchemy.orm import Session

from models.listing.facade import ListingFacade
from models.listing_financial_report.facade import ListingFinancialReportFacade
from models.property.entity import PropertyEntity
from models.property.facade import PropertyFacade
from models.property_comp.facade import PropertyCompFacade
from models.property_financial_report.entity import PropertyFinancialReportEntity
from models.property_financial_report.facade import PropertyFinancialReportFacade
from services import airroi
from services.calculations import (
    AnalysisResult,
    PropertyScenario,
    analyze,
    conservative_of,
)
from services.exceptions import AirROIError
from services.exchange_rate import convert_cop_to_usd, resolve_cop_per_usd
from services.geo import haversine_km
from utils.logging.extended_logger import ExtendedLogger

logger = cast(ExtendedLogger, logging.getLogger(__name__))

DAYS_PER_YEAR = 365

MIN_COMP_COUNT = 5
"""
Fewer surviving comps than this and there is no comp-derived estimate at all.

Both Calima captures came back with a single comparable - the same 5br/5.5ba
property, returned for a 2br query and a 3br query alike, because AirROI stops
honouring the filters when the local pool is thin. A median over one listing is
not an estimate, and the response says nothing to warn you. Returning ``None`` is
the point; do not "fix" it into a number.
"""

COMP_REVENUE_TOLERANCE = 0.10
"""
How far a comp's ``adr x occupancy x ttm_total_days`` may stray from its reported
``ttm_revenue`` before the comp is dropped.

``ttm_total_days`` is a data-quality gate, not a multiplier: a listing that was
only live for part of the year has a trailing-twelve-month revenue that cannot be
projected forward to a full year, and one whose three reported figures do not
reconcile cannot be trusted for either.
"""

GUESTS_PER_BEDROOM = 2
"""
Stand-in when ``properties.guests`` is unset - Finca Raiz never publishes it.

The captured comps put the median at 8 guests for a 3-bedroom property, so this
understates by around 25% there. That is the conservative direction: it biases
the comp set toward smaller units and revenue downward.
"""

PEAK_MONTH_COUNT = 3

# Hardcoded rather than taken from ``calendar.month_name``, which renders in the
# process locale - the column holds English names and a container with a
# different ``LC_TIME`` would quietly start writing them in another language.
MONTH_NAMES = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)

REVENUE_SOURCE_AIRROI_P25 = "airroi_p25"
REVENUE_SOURCE_AIRROI_AVG = "airroi_avg"
REVENUE_SOURCE_COMP_DERIVED = "comp_derived"
THIN_COMPS_SUFFIX = "_thin_comps"


def analyze_property(
    db_session: Session,
    *,
    property_id: UUID | str,
    overrides: Optional[dict[str, Any]] = None,
) -> PropertyFinancialReportEntity:
    """
    Analyses a stored property and persists the result.

    ``overrides`` carries any ``PropertyScenario`` field the caller wants to set -
    down payment, interest rate, HOA and so on. Anything absent falls back to the
    Part 6 defaults in ``constants.colombia``. ``annual_revenue_cop`` is ignored
    if passed: deriving it is the whole job.

    Raises ``PropertyFacade.NoResultFound`` for an unknown property, ``ValueError``
    when the property cannot supply an input the analysis needs (no bath count, no
    purchase price, no exchange rate), and ``AirROIError`` when the upstream call
    fails or comes back without a revenue figure.
    """
    overrides = overrides or {}
    captured_at = datetime.now(timezone.utc)

    property_record = PropertyFacade(db_session=db_session).get_one_by_id(property_id)

    baths = _resolve_baths(property_record)
    guests = _resolve_guests(property_record)
    purchase_price_cop = _resolve_purchase_price(property_record, overrides)
    cop_per_usd = _resolve_cop_per_usd(db_session, property_record)

    estimate = airroi.get_revenue_estimate(
        latitude=property_record.latitude,
        longitude=property_record.longitude,
        bedrooms=property_record.bedrooms,
        baths=baths,
        guests=guests,
    )

    comps = list(estimate.get("comparable_listings") or [])
    projections = _projections(comps)

    if len(projections) < MIN_COMP_COUNT:
        logger.info(
            f"Only {len(projections)} of {len(comps)} inline comps are usable for "
            f"property with id='{property_record.id}' - retrying against "
            f"/listings/comparables"
        )
        comps = _merge_comps(
            comps,
            _fallback_comps(property_record, baths=baths, guests=guests),
        )
        projections = _projections(comps)

    _persist_comps(
        db_session,
        property_record=property_record,
        comps=comps,
        captured_at=captured_at,
    )

    comp_derived_revenue_cop = (
        statistics.median(projections) if len(projections) >= MIN_COMP_COUNT else None
    )

    revenue_percentiles = (estimate.get("percentiles") or {}).get("revenue") or {}
    airroi_revenue_cop, airroi_source = _airroi_candidate(estimate, revenue_percentiles)

    scenario_fields = _scenario_fields(
        overrides, purchase_price_cop=purchase_price_cop, cop_per_usd=cop_per_usd
    )
    scenario = PropertyScenario(
        **scenario_fields, annual_revenue_cop=airroi_revenue_cop
    )

    # Insertion order matters: ``conservative_of`` keeps the first of equal
    # candidates, so a dead heat resolves to AirROI's own figure rather than to
    # whichever happened to be built second.
    results: dict[str, AnalysisResult] = {airroi_source: analyze(scenario)}
    if comp_derived_revenue_cop is not None:
        results[REVENUE_SOURCE_COMP_DERIVED] = analyze(
            scenario.model_copy(update={"annual_revenue_cop": comp_derived_revenue_cop})
        )

    winner = conservative_of(*results.values())
    annual_revenue_source = next(
        source for source, result in results.items() if result is winner
    )

    if comp_derived_revenue_cop is None:
        # There was no contest - say so, rather than leaving a source name that
        # implies AirROI's estimate beat something.
        annual_revenue_source = f"{airroi_source}{THIN_COMPS_SUFFIX}"

    logger.info(
        f"Analysed property with id='{property_record.id}' using "
        f"'{annual_revenue_source}' over {len(projections)} usable comps"
    )

    return PropertyFinancialReportFacade(db_session=db_session).create_or_update(
        payload=_report_payload(
            property_record=property_record,
            scenario=scenario,
            winner=winner,
            annual_revenue_source=annual_revenue_source,
            cop_per_usd=cop_per_usd,
            calculated_at=captured_at,
            estimate=estimate,
            revenue_percentiles=revenue_percentiles,
            comp_derived_revenue_cop=comp_derived_revenue_cop,
            comp_count=len(projections),
        )
    )


def _resolve_baths(property_record: PropertyEntity) -> float:
    """
    Column first, then the ``notes`` JSON Step 4 stashed bathrooms in.

    Raises rather than guessing: ``/calculator/estimate`` requires a bath count,
    and a made-up one silently changes which comps come back.
    """
    if property_record.baths is not None:
        return float(property_record.baths)

    from_notes = _notes_number(property_record.notes, "bathrooms")
    if from_notes is not None:
        logger.info(
            f"Property with id='{property_record.id}' has no 'baths' column - "
            f"read {from_notes} from its 'notes'"
        )
        return float(from_notes)

    raise ValueError(
        f"Property with id='{property_record.id}' has no bath count, which AirROI "
        f"requires. Set 'baths' on the property and try again."
    )


def _resolve_guests(property_record: PropertyEntity) -> int:
    if property_record.guests is not None:
        return int(property_record.guests)

    guests = int(property_record.bedrooms) * GUESTS_PER_BEDROOM
    logger.warning(
        f"Property with id='{property_record.id}' has no 'guests' - assuming "
        f"{property_record.bedrooms} bedrooms x {GUESTS_PER_BEDROOM} = {guests}. "
        f"This biases the comp set toward smaller units."
    )

    return guests


def _resolve_purchase_price(
    property_record: PropertyEntity, overrides: dict[str, Any]
) -> float:
    purchase_price_cop = (
        overrides.get("purchase_price_cop") or property_record.purchase_price_cop
    )

    if not purchase_price_cop or purchase_price_cop <= 0:
        raise ValueError(
            f"Property with id='{property_record.id}' has no purchase price to "
            f"analyse against (status='{property_record.status}'). Supply "
            f"'purchase_price_cop' with the request."
        )

    return float(purchase_price_cop)


def _resolve_cop_per_usd(db_session: Session, property_record: PropertyEntity) -> float:
    """
    Our own rate, never AirROI's, so that one rate explains every ``_usd`` column.
    """
    exchange_rate = resolve_cop_per_usd(db_session)

    if exchange_rate is None or not exchange_rate.cop_per_usd:
        raise ValueError(
            f"No COP/USD exchange rate available, so property with "
            f"id='{property_record.id}' cannot be analysed"
        )

    return float(exchange_rate.cop_per_usd)


def _notes_number(notes: Optional[str], key: str) -> Optional[float]:
    """Reads a numeric key out of the ``notes`` JSON blob, tolerating free text."""
    if not notes:
        return None

    try:
        parsed = json.loads(notes)
    except (TypeError, ValueError):
        # ``notes`` is free text and is not always JSON - the properties route
        # accepts a plain sentence there.
        return None

    if not isinstance(parsed, dict):
        return None

    value = parsed.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None

    return float(value)


def _projections(comps: list[dict[str, Any]]) -> list[float]:
    """Forward-projected annual revenue for every comp that survives the gate."""
    projections = []

    for comp in comps:
        projection = _projected_revenue_cop(comp)
        if projection is not None:
            projections.append(projection)

    return projections


def _projected_revenue_cop(comp: dict[str, Any]) -> Optional[float]:
    metrics = comp.get("performance_metrics") or {}
    airroi_id = (comp.get("listing_info") or {}).get("listing_id")

    adr_cop = metrics.get("ttm_avg_rate")
    occupancy_rate = metrics.get("ttm_occupancy")
    ttm_total_days = metrics.get("ttm_total_days")
    ttm_revenue_cop = metrics.get("ttm_revenue")

    if adr_cop is None or occupancy_rate is None:
        logger.info(
            f"Comp with airroi_id='{airroi_id}' reports no ADR or occupancy - "
            f"excluded from the comp-derived estimate"
        )
        return None

    if not ttm_total_days or not ttm_revenue_cop:
        logger.info(
            f"Comp with airroi_id='{airroi_id}' has no trailing-twelve-month "
            f"revenue to reconcile against - excluded from the comp-derived estimate"
        )
        return None

    implied_ttm_revenue_cop = adr_cop * occupancy_rate * ttm_total_days
    gap = abs(implied_ttm_revenue_cop - ttm_revenue_cop) / abs(ttm_revenue_cop)

    if gap > COMP_REVENUE_TOLERANCE:
        logger.info(
            f"Comp with airroi_id='{airroi_id}' does not reconcile - "
            f"adr x occupancy x {ttm_total_days:g} days implies "
            f"{implied_ttm_revenue_cop:,.0f} COP against a reported "
            f"{ttm_revenue_cop:,.0f} COP ({gap:.1%} apart) - excluded from the "
            f"comp-derived estimate"
        )
        return None

    return adr_cop * occupancy_rate * DAYS_PER_YEAR


def _fallback_comps(
    property_record: PropertyEntity, *, baths: float, guests: int
) -> list[dict[str, Any]]:
    """
    One retry against ``/listings/comparables`` when the inline set is too thin.

    Best-effort by design: the primary estimate has already succeeded, so a
    failure here costs a comp-derived figure rather than the whole report.
    """
    try:
        response = airroi.get_comparables(
            latitude=property_record.latitude,
            longitude=property_record.longitude,
            bedrooms=property_record.bedrooms,
            baths=baths,
            guests=guests,
        )
    except AirROIError as exc:
        logger.warning(
            f"Fallback comparables lookup failed for property with "
            f"id='{property_record.id}': {exc}"
        )
        return []

    # No capture of this endpoint exists to pin the key down, and the two
    # endpoints that are captured disagree with each other - ``/calculator/estimate``
    # nests its comps under ``comparable_listings`` and ``/listings/search/market``
    # under ``results``. Accept either rather than guess.
    return list(response.get("results") or response.get("comparable_listings") or [])


def _merge_comps(
    primary: list[dict[str, Any]], fallback: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Adds fallback comps that the inline set did not already contain."""
    merged = {
        (comp.get("listing_info") or {}).get("listing_id"): comp for comp in primary
    }

    for comp in fallback:
        airroi_id = (comp.get("listing_info") or {}).get("listing_id")
        if airroi_id is not None and airroi_id not in merged:
            merged[airroi_id] = comp

    merged.pop(None, None)

    return list(merged.values())


def _persist_comps(
    db_session: Session,
    *,
    property_record: PropertyEntity,
    comps: list[dict[str, Any]],
    captured_at: datetime,
) -> int:
    """
    Writes each comp as a listing, a listing financial report and a join row.

    Each comp gets its own ``SAVEPOINT``. Without one, a single malformed
    comparable would poison the request's transaction and lose the report too -
    and the crons' ``rollback(); commit()`` trick is not available here, because
    the session belongs to the route.
    """
    listing_facade = ListingFacade(db_session=db_session)
    listing_financial_report_facade = ListingFinancialReportFacade(
        db_session=db_session
    )
    property_comp_facade = PropertyCompFacade(db_session=db_session)

    persisted = 0

    for comp in comps:
        airroi_id = (comp.get("listing_info") or {}).get("listing_id")

        try:
            with db_session.begin_nested():
                listing_record = listing_facade.create_or_update(
                    payload=_listing_payload(comp)
                )
                listing_financial_report_facade.create_or_update(
                    payload={
                        "listing_id": listing_record.id,
                        **_listing_financial_report_payload(comp),
                    }
                )
                property_comp_facade.create_or_update(
                    payload=_property_comp_payload(
                        comp,
                        property_record=property_record,
                        listing_id=listing_record.id,
                        captured_at=captured_at,
                    )
                )
            persisted += 1
        except Exception:
            logger.exception(
                f"Could not persist comp with airroi_id='{airroi_id}' for property "
                f"with id='{property_record.id}'"
            )
            continue

    logger.info(
        f"Persisted {persisted} of {len(comps)} comps for property with "
        f"id='{property_record.id}'"
    )

    return persisted


def _listing_payload(comp: dict[str, Any]) -> dict[str, Any]:
    listing_info = comp["listing_info"]
    location_info = comp["location_info"]
    property_details = comp.get("property_details") or {}

    latitude = location_info["latitude"]
    longitude = location_info["longitude"]

    # ``market_id`` is deliberately absent. A comp comes back from a coordinate
    # lookup, not from one of our markets, and ``ListingFacade.create_or_update``
    # merges over the existing row - so a comp that the nightly ingest already
    # owns keeps the market it was ingested under.
    return {
        "airroi_id": listing_info["listing_id"],
        "amenities": property_details.get("amenities", []),
        "baths": property_details.get("baths", None),
        "beds": property_details.get("beds", None),
        "bedrooms": property_details["bedrooms"],
        "cover_photo_url": listing_info.get("cover_photo_url", None),
        "description": listing_info.get("description", None),
        "latitude": latitude,
        "location": f"POINT({longitude} {latitude})",
        "longitude": longitude,
        "name": listing_info.get("listing_name", None),
        "photo_urls": listing_info.get("photo_urls", []),
        "property_type": listing_info["listing_type"],
    }


def _listing_financial_report_payload(comp: dict[str, Any]) -> dict[str, Any]:
    """
    The same key renaming ``handle_listings_by_market`` does.

    AirROI calls them ``num_reviews`` and ``ttm_occupancy``; the columns are
    ``number_of_reviews`` and ``ttm_occupancy_rate``. Everything else passes
    through under its own name.
    """
    ratings = dict(comp.get("ratings", {}) or {})
    ratings["number_of_reviews"] = ratings.pop("num_reviews", None)

    metrics = dict(comp.get("performance_metrics", {}) or {})
    metrics["ttm_occupancy_rate"] = metrics.pop("ttm_occupancy", None)
    metrics["ttm_adjusted_occupancy_rate"] = metrics.pop("ttm_adjusted_occupancy", None)
    metrics["l90d_occupancy_rate"] = metrics.pop("l90d_occupancy", None)
    metrics["l90d_adjusted_occupancy_rate"] = metrics.pop(
        "l90d_adjusted_occupancy", None
    )

    return {**ratings, **metrics}


def _property_comp_payload(
    comp: dict[str, Any],
    *,
    property_record: PropertyEntity,
    listing_id: UUID,
    captured_at: datetime,
) -> dict[str, Any]:
    location_info = comp.get("location_info") or {}
    metrics = comp.get("performance_metrics") or {}

    latitude = location_info.get("latitude")
    longitude = location_info.get("longitude")

    # ``None`` rather than a distance of zero when a comp arrives without
    # coordinates - 0.0 is a real measurement for a comp next door.
    distance_km = (
        haversine_km(
            property_record.latitude, property_record.longitude, latitude, longitude
        )
        if latitude is not None and longitude is not None
        else None
    )

    return {
        "property_id": property_record.id,
        "listing_id": listing_id,
        "adr_cop": metrics.get("ttm_avg_rate"),
        "captured_at": captured_at,
        "distance_km": distance_km,
        "occupancy_rate": metrics.get("ttm_occupancy"),
        "ttm_revenue_cop": metrics.get("ttm_revenue"),
        "ttm_total_days": metrics.get("ttm_total_days"),
    }


def _airroi_candidate(
    estimate: dict[str, Any], revenue_percentiles: dict[str, Any]
) -> tuple[float, str]:
    """
    AirROI's own revenue candidate - ``p25``, not the headline figure.

    ``revenue`` equals ``percentiles.revenue.avg`` exactly, and the distribution
    is right-skewed: on the Salento 3br capture the mean sits 12% above the median
    and the p90 is nearly double it. A mean over that shape is not a plausible
    outcome, so p25 is what gets analysed and the mean is stored beside it for
    reference.
    """
    p25 = revenue_percentiles.get("p25")
    if p25 is not None:
        return float(p25), REVENUE_SOURCE_AIRROI_P25

    average = revenue_percentiles.get("avg") or estimate.get("revenue")
    if average is not None:
        logger.warning(
            "AirROI returned no 'percentiles.revenue.p25' - falling back to the "
            "mean, which overstates a right-skewed distribution"
        )
        return float(average), REVENUE_SOURCE_AIRROI_AVG

    raise AirROIError("AirROI returned no revenue figure to analyse")


def _scenario_fields(
    overrides: dict[str, Any], *, purchase_price_cop: float, cop_per_usd: float
) -> dict[str, Any]:
    fields = {
        key: value
        for key, value in overrides.items()
        if key in PropertyScenario.model_fields and value is not None
        # Set below and derived respectively - an override of either would be
        # answering the question this module exists to ask.
        and key not in ("purchase_price_cop", "annual_revenue_cop")
    }
    fields["purchase_price_cop"] = purchase_price_cop
    fields["cop_per_usd"] = cop_per_usd

    return fields


def _peak_months(distribution: list[float]) -> list[str]:
    """
    The three months with the largest share of annual revenue.

    Top-3 rather than the execution plan's "15% above the annual average" rule,
    which returns an empty list for the Bogota 2br capture - no month there clears
    the threshold. Top-3 always answers. Ties resolve to the earlier month,
    because ``sorted`` is stable.
    """
    if not distribution:
        return []

    ranked = sorted(
        enumerate(distribution[: len(MONTH_NAMES)]),
        key=lambda pair: pair[1],
        reverse=True,
    )

    return [MONTH_NAMES[index] for index, _ in ranked[:PEAK_MONTH_COUNT]]


def _report_payload(
    *,
    property_record: PropertyEntity,
    scenario: PropertyScenario,
    winner: AnalysisResult,
    annual_revenue_source: str,
    cop_per_usd: float,
    calculated_at: datetime,
    estimate: dict[str, Any],
    revenue_percentiles: dict[str, Any],
    comp_derived_revenue_cop: Optional[float],
    comp_count: int,
) -> dict[str, Any]:
    """
    Flattens a scenario and its winning result into ``property_financial_reports``.

    The scenario's own knobs are stored alongside the outputs so that a report
    stays readable after someone edits the property or changes a default in
    ``constants.colombia`` - the row explains itself rather than depending on
    what the rest of the database happens to say today.

    NOTE: ``comp_count`` is the number of comps that survived the reconciliation
    gate, not the number persisted. It is the figure ``MIN_COMP_COUNT`` is
    compared against, and therefore the one that explains why
    ``comp_derived_revenue_cop`` is or is not set; the full set is in
    ``property_comps``.
    """
    monthly_expenses = winner.monthly_expenses

    return {
        "property_id": property_record.id,
        # --- inputs the report was run against
        "assessed_value_cop": scenario.assessed_value_cop,
        "closing_costs_percentage": scenario.closing_costs_percentage,
        "down_payment_percentage": scenario.down_payment_percentage,
        "hoa_monthly_cop": scenario.hoa_monthly_cop,
        "interest_rate": scenario.interest_rate_percentage,
        "loan_term_years": scenario.loan_term_years,
        "maintenance_reserve_percentage": scenario.maintenance_reserve_percentage,
        "management_fee_percentage": scenario.management_fee_percentage,
        "predial_rate_percentage": scenario.predial_rate_percentage,
        "purchase_price_cop": scenario.purchase_price_cop,
        "renovation_budget_cop": scenario.renovation_budget_cop,
        # --- results
        "annual_net_income_cop": winner.annual_net_income_cop,
        "annual_net_income_usd": convert_cop_to_usd(
            winner.annual_net_income_cop, cop_per_usd
        ),
        "annual_revenue_cop": winner.annual_revenue_cop,
        "annual_revenue_source": annual_revenue_source,
        "annual_revenue_usd": convert_cop_to_usd(
            winner.annual_revenue_cop, cop_per_usd
        ),
        "calculated_at": calculated_at,
        "cash_invested_cop": winner.cash_invested_cop,
        "cash_invested_usd": convert_cop_to_usd(winner.cash_invested_cop, cop_per_usd),
        "coc_return_percentage": winner.coc_return_percentage,
        "exchange_rate": cop_per_usd,
        "monthly_expenses_cop": monthly_expenses.total_cop,
        "monthly_expenses_usd": convert_cop_to_usd(
            monthly_expenses.total_cop, cop_per_usd
        ),
        "monthly_mortgage_cop": monthly_expenses.mortgage_cop,
        "payback_years": winner.payback_years,
        # --- provenance
        "airroi_adr_cop": estimate.get("average_daily_rate"),
        "airroi_occupancy_rate": estimate.get("occupancy"),
        "airroi_revenue_cop": revenue_percentiles.get("avg", estimate.get("revenue")),
        "airroi_revenue_p25_cop": revenue_percentiles.get("p25"),
        "airroi_revenue_p50_cop": revenue_percentiles.get("p50"),
        "airroi_revenue_p75_cop": revenue_percentiles.get("p75"),
        "airroi_revenue_p90_cop": revenue_percentiles.get("p90"),
        "comp_count": comp_count,
        "comp_derived_revenue_cop": comp_derived_revenue_cop,
        "monthly_revenue_distribution": estimate.get("monthly_revenue_distributions"),
        "peak_months": _peak_months(
            estimate.get("monthly_revenue_distributions") or []
        ),
    }
