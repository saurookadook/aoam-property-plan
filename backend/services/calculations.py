"""
Turns a purchase price and a revenue estimate into cash-on-cash return and
payback period.

Pure and dependency-free by design: no DB session, no HTTP, no clock. Callers
supply an exchange rate off an ``exchange_rates`` row rather than the module
holding a constant, and ``calculated_at`` is stamped by whoever persists the
result, not here.

Everything is computed in COP and returned in COP. ``AnalysisResult`` echoes back
the ``cop_per_usd`` it was built with so the persistence layer can fill the
``_usd`` columns with ``services.exchange_rate.convert_cop_to_usd`` without having
to remember which rate applied. Percentages are whole numbers - ``10.0`` is 10% -
and nothing is rounded on the way out.

NOTE: debt service counts in full, principal included. That is the standard
cash-on-cash convention and it makes the figure deliberately conservative; it is
not an oversight to be "fixed" to interest-only.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from constants.colombia import (
    DEFAULT_CLOSING_COSTS_PERCENTAGE,
    DEFAULT_DOWN_PAYMENT_PERCENTAGE,
    DEFAULT_HOA_MONTHLY_COP,
    DEFAULT_INTEREST_RATE_PERCENTAGE,
    DEFAULT_LOAN_TERM_YEARS,
    DEFAULT_MAINTENANCE_RESERVE_PERCENTAGE,
    DEFAULT_MANAGEMENT_FEE_PERCENTAGE,
    DEFAULT_PREDIAL_RATE_PERCENTAGE,
)


class PropertyScenario(BaseModel):
    """
    Every input one analysis run needs, with Part 6's assumptions as defaults.

    Frozen for two reasons. The sensitivity sweep varies revenue by rebuilding the
    scenario through ``model_copy(update=...)``, and a shared mutable scenario
    would let one variant's edit leak into the next; and an immutable input makes
    it safe to hand the same scenario to several calculations without defensive
    copying.

    ``assessed_value_cop`` is kept separate from ``purchase_price_cop`` because
    predial is levied on the cadastral (avaluo catastral) value, which in Colombia
    routinely sits well below what a property actually sells for. Leaving it unset
    resolves it to the purchase price - the conservative reading, since it can only
    overstate the tax.
    """

    # ``validate_default`` so the Part 6 constants are bounds-checked on the way in
    # too - editing a rate in ``constants.colombia`` to something impossible should
    # fail loudly here rather than quietly produce a nonsense return.
    model_config = ConfigDict(frozen=True, validate_default=True)

    purchase_price_cop: float = Field(gt=0)
    annual_revenue_cop: float = Field(ge=0)
    cop_per_usd: float = Field(gt=0)

    assessed_value_cop: Optional[float] = Field(default=None, gt=0)
    hoa_monthly_cop: float = Field(default=DEFAULT_HOA_MONTHLY_COP, ge=0)
    renovation_budget_cop: float = Field(default=0.0, ge=0)

    # 100% down is allowed and means no loan at all, so the upper bound is
    # inclusive; a zero interest rate is likewise legitimate (seller financing).
    down_payment_percentage: float = Field(
        default=DEFAULT_DOWN_PAYMENT_PERCENTAGE, ge=0, le=100
    )
    interest_rate_percentage: float = Field(
        default=DEFAULT_INTEREST_RATE_PERCENTAGE, ge=0, le=100
    )
    loan_term_years: float = Field(default=DEFAULT_LOAN_TERM_YEARS, gt=0)
    management_fee_percentage: float = Field(
        default=DEFAULT_MANAGEMENT_FEE_PERCENTAGE, ge=0, le=100
    )
    maintenance_reserve_percentage: float = Field(
        default=DEFAULT_MAINTENANCE_RESERVE_PERCENTAGE, ge=0, le=100
    )
    closing_costs_percentage: float = Field(
        default=DEFAULT_CLOSING_COSTS_PERCENTAGE, ge=0, le=100
    )
    predial_rate_percentage: float = Field(
        default=DEFAULT_PREDIAL_RATE_PERCENTAGE, ge=0, le=100
    )

    @model_validator(mode="before")
    @classmethod
    def resolve_assessed_value(cls, data: Any) -> Any:
        """
        Fills ``assessed_value_cop`` from the purchase price when it was not given.

        Done here rather than at each point of use so that no downstream code has
        to branch on ``None`` - by the time a scenario exists, the field is a
        number, and predial can be computed unconditionally.

        This runs ``before`` rather than ``after`` because the model is frozen: an
        after-validator could neither assign the field nor return a replacement
        instance, which pydantic rejects outright when validating via ``__init__``.
        Copying the raw value across means it still goes through the field's own
        ``gt=0`` check, so a bad purchase price is caught either way.
        """
        if isinstance(data, dict) and data.get("assessed_value_cop") is None:
            purchase_price_cop = data.get("purchase_price_cop")
            if purchase_price_cop is not None:
                return {**data, "assessed_value_cop": purchase_price_cop}

        return data


class MonthlyExpenseBreakdown(BaseModel):
    """
    The monthly cost lines behind a single total, all in COP.

    Carried as a breakdown rather than one number because the analysis panel shows
    the lines, and because a total on its own gives no way to see which assumption
    is driving a poor return.

    ``total_cop`` is derived rather than supplied: it is the sum by definition, and
    a stored copy could only ever drift from its parts.
    """

    model_config = ConfigDict(frozen=True)

    mortgage_cop: float
    hoa_cop: float
    management_fee_cop: float
    maintenance_reserve_cop: float
    predial_cop: float

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_cop(self) -> float:
        return (
            self.mortgage_cop
            + self.hoa_cop
            + self.management_fee_cop
            + self.maintenance_reserve_cop
            + self.predial_cop
        )


class AnalysisResult(BaseModel):
    """
    One analysed scenario.

    A superset of ``property_financial_reports``: the expense breakdown and the
    monthly mortgage figure inside it have no columns yet, so persistence selects
    the subset that maps and the rest stays available to the UI.

    ``cop_per_usd`` is echoed from the scenario so that whoever writes the row has
    the rate for both the ``_usd`` columns and the ``exchange_rate`` column,
    without re-resolving a rate that may since have moved.
    """

    model_config = ConfigDict(frozen=True)

    cop_per_usd: float
    annual_revenue_cop: float
    monthly_expenses: MonthlyExpenseBreakdown
    annual_net_income_cop: float
    cash_invested_cop: float
    coc_return_percentage: float
    payback_years: Optional[float]


class SensitivityCell(BaseModel):
    """
    One column of the sensitivity sweep - the same scenario at scaled revenue.

    A single revenue axis rather than the ADR-by-occupancy grid the doc describes:
    revenue is ADR x occupancy x 365, so scaling either input scales the same
    product and a two-dimensional grid would repeat its own values.
    """

    model_config = ConfigDict(frozen=True)

    revenue_factor: float
    annual_revenue_cop: float
    coc_return_percentage: float
    payback_years: Optional[float]
