from __future__ import annotations

from typing import Optional

from models.base.entity import BaseEntityModel
from models.market_financial_report.entity import MarketFinancialReportEntity
from models.mixins import TimestampsEntityMixin


class MarketEntity(BaseEntityModel, TimestampsEntityMixin):
    country: str
    district: Optional[str]
    locality: str
    region: str


class MarketWithFinancialReportEntity(MarketEntity):
    """
    A market card's worth of data: the four geographic strings, the latest
    figures, and where to put the marker.

    Deliberately a subclass rather than extra fields on ``MarketEntity``.
    ``MarketEntity`` is what ``/markets/{id}`` returns and what three cron
    handlers pass around; widening it would oblige every one of those callers to
    produce a report they have no reason to hold. ``HighestEarningListingEntity``
    sets the same precedent on the listing side.

    ``latitude``/``longitude`` are the centroid of the market's ingested
    listings - the same average ``MarketFacade.get_centroid_by_id`` computes -
    and are ``None`` for a market with nothing ingested. ``financial_report`` is
    ``None`` for a market that has never been summarised. Both absences are
    ordinary states of a freshly seeded roster, not errors.
    """

    financial_report: Optional[MarketFinancialReportEntity] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
