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
    MONTHS_PER_YEAR,
)

# One revenue axis, not the doc's ADR-by-occupancy grid - see ``SensitivityCell``.
DEFAULT_SENSITIVITY_FACTORS = (0.9, 1.0, 1.1)


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


def loan_principal(
    purchase_price_cop: float,
    down_payment_percentage: float = DEFAULT_DOWN_PAYMENT_PERCENTAGE,
) -> float:
    """
    The borrowed portion of the purchase price.

    Separated out so ``analyze`` composes named steps rather than carrying a bare
    multiplication of its own, and so the 100%-down case has one obvious home: it
    returns ``0.0``, which ``mortgage_payment`` then turns into a zero payment.
    """
    if purchase_price_cop <= 0:
        raise ValueError(
            f"purchase_price_cop must be greater than 0, got {purchase_price_cop}"
        )

    return purchase_price_cop * (1 - down_payment_percentage / 100)


def mortgage_payment(
    principal_cop: float,
    annual_rate_percentage: float = DEFAULT_INTEREST_RATE_PERCENTAGE,
    term_years: float = DEFAULT_LOAN_TERM_YEARS,
) -> float:
    """
    The level monthly payment that amortises ``principal_cop`` over the term.

    The standard annuity formula, ``P·r / (1 − (1+r)^−n)``, with ``r`` the monthly
    rate and ``n`` the number of payments.

    Two cases fall outside it. A zero interest rate collapses the denominator to
    zero, so the payment is the principal spread evenly - ``principal / n`` - not a
    division by zero. And a zero principal (a cash purchase, or 100% down) is not a
    degenerate loan but the absence of one, so it costs ``0.0``.

    NOTE: the doc's Part 4 row 5 quotes ~USD 1,540/month for a COP 500M finca at
    30% down, 10%, 15 years. That is unreachable: those inputs give COP
    3,761,117.91, or USD 906.29 at 4,150 COP/USD. The doc is wrong, not this.
    """
    if term_years <= 0:
        raise ValueError(f"term_years must be greater than 0, got {term_years}")

    if principal_cop < 0:
        raise ValueError(f"principal_cop cannot be negative, got {principal_cop}")

    if principal_cop == 0:
        return 0.0

    payment_count = term_years * MONTHS_PER_YEAR
    monthly_rate = annual_rate_percentage / 100 / MONTHS_PER_YEAR

    if monthly_rate == 0:
        return principal_cop / payment_count

    return principal_cop * monthly_rate / (1 - (1 + monthly_rate) ** -payment_count)


def annual_predial(
    assessed_value_cop: float,
    predial_rate_percentage: float = DEFAULT_PREDIAL_RATE_PERCENTAGE,
) -> float:
    """
    Predial - Colombian property tax - for one year.

    Part 6 defines this at 0.8% of assessed value per year, but Step 5's expense
    list omits it entirely. Leaving it out is not neutral: on a COP 500M property
    it overstates monthly net income by COP 333,333, which is enough to move a
    marginal deal from red to black. So it is charged here.

    It is levied on the cadastral value (*avaluo catastral*), which is why this
    takes an assessed value rather than the purchase price - the two routinely
    differ in Colombia, with the cadastral figure the lower of the pair.
    """
    return assessed_value_cop * predial_rate_percentage / 100


def closing_costs(
    purchase_price_cop: float,
    closing_costs_percentage: float = DEFAULT_CLOSING_COSTS_PERCENTAGE,
) -> float:
    """
    One-off cost of completing the purchase - notary, registration, escritura.

    Part 6's 2.75% is the midpoint of the 2.5-3% Colombian range.
    """
    if purchase_price_cop <= 0:
        raise ValueError(
            f"purchase_price_cop must be greater than 0, got {purchase_price_cop}"
        )

    return purchase_price_cop * closing_costs_percentage / 100


def cash_invested(
    purchase_price_cop: float,
    down_payment_percentage: float = DEFAULT_DOWN_PAYMENT_PERCENTAGE,
    closing_costs_percentage: float = DEFAULT_CLOSING_COSTS_PERCENTAGE,
    renovation_budget_cop: float = 0.0,
) -> float:
    """
    Total cash out of pocket - the denominator of cash-on-cash return.

    Both ``coc_return`` and ``payback_period`` consume this figure and the doc
    supplies no function that produces it, which is the gap this closes. It is
    everything paid up front and not borrowed: the down payment, the closing costs,
    and any renovation the property needs before it can earn.
    """
    down_payment_cop = purchase_price_cop * down_payment_percentage / 100

    return (
        down_payment_cop
        + closing_costs(purchase_price_cop, closing_costs_percentage)
        + renovation_budget_cop
    )


def monthly_expenses(
    mortgage_cop: float,
    hoa_monthly_cop: float = DEFAULT_HOA_MONTHLY_COP,
    annual_revenue_cop: float = 0.0,
    purchase_price_cop: float = 0.0,
    assessed_value_cop: Optional[float] = None,
    management_fee_percentage: float = DEFAULT_MANAGEMENT_FEE_PERCENTAGE,
    maintenance_reserve_percentage: float = DEFAULT_MAINTENANCE_RESERVE_PERCENTAGE,
    predial_rate_percentage: float = DEFAULT_PREDIAL_RATE_PERCENTAGE,
) -> MonthlyExpenseBreakdown:
    """
    Every recurring monthly cost, itemised.

    Returns the breakdown rather than a single number because a bad return is only
    actionable once you can see which line caused it - and because the analysis
    panel renders the lines individually.

    Three of the five are annual figures divided by twelve. The management fee is
    charged on *gross* revenue, not net, which is how Colombian STR managers
    actually bill; taking it off net would understate it. Maintenance is a reserve
    against the purchase price rather than a real invoice, so it is charged whether
    or not anything broke this month. Predial follows ``annual_predial``, defaulting
    its basis to the purchase price when no assessed value is known.
    """
    if purchase_price_cop <= 0:
        raise ValueError(
            f"purchase_price_cop must be greater than 0, got {purchase_price_cop}"
        )

    if assessed_value_cop is None:
        assessed_value_cop = purchase_price_cop

    management_fee_cop = (
        annual_revenue_cop * management_fee_percentage / 100 / MONTHS_PER_YEAR
    )
    maintenance_reserve_cop = (
        purchase_price_cop * maintenance_reserve_percentage / 100 / MONTHS_PER_YEAR
    )
    predial_cop = (
        annual_predial(assessed_value_cop, predial_rate_percentage) / MONTHS_PER_YEAR
    )

    return MonthlyExpenseBreakdown(
        mortgage_cop=mortgage_cop,
        hoa_cop=hoa_monthly_cop,
        management_fee_cop=management_fee_cop,
        maintenance_reserve_cop=maintenance_reserve_cop,
        predial_cop=predial_cop,
    )


def annual_net_income(annual_revenue_cop: float, monthly_expenses_cop: float) -> float:
    """
    Gross annual revenue less a full year of expenses.

    Goes negative freely, and is meant to: a property that cannot carry its own
    mortgage is exactly what this module exists to surface.
    """
    return annual_revenue_cop - monthly_expenses_cop * MONTHS_PER_YEAR


def coc_return(annual_net_income_cop: float, cash_invested_cop: float) -> float:
    """
    Cash-on-cash return as a whole-number percentage - ``4.5`` means 4.5%.

    A loss returns the real negative figure rather than being floored at zero,
    because "-14%" and "0%" call for very different decisions.

    Zero cash invested raises instead of returning infinity. It is reachable - 0%
    down with 0% closing costs - and a return on nothing is not a percentage; a
    caller who lands here has a modelling error rather than an infinitely good deal.
    """
    if cash_invested_cop <= 0:
        raise ValueError(
            "cash_invested_cop must be greater than 0 to express a return as a "
            f"percentage, got {cash_invested_cop}"
        )

    return annual_net_income_cop / cash_invested_cop * 100


def payback_period(
    cash_invested_cop: float, annual_net_income_cop: float
) -> Optional[float]:
    """
    Years for net income to repay the cash invested, or ``None`` if it never does.

    ``None`` rather than a negative number or ``inf`` when net income is zero or
    negative. Both alternatives sort as though the property pays back *quickly* -
    a negative payback beats every positive one in an ascending sort, and ``inf``
    does not survive the ``NUMERIC`` round-trip cleanly. ``None`` maps to SQL
    ``NULL``, which is what "does not pay back" actually means.
    """
    if annual_net_income_cop <= 0:
        return None

    return cash_invested_cop / annual_net_income_cop


def analyze(scenario: PropertyScenario) -> AnalysisResult:
    """
    Runs one scenario end to end.

    Composition only - every figure below comes from a function above, so there is
    exactly one place to change any given rule.
    """
    principal_cop = loan_principal(
        scenario.purchase_price_cop, scenario.down_payment_percentage
    )
    mortgage_cop = mortgage_payment(
        principal_cop,
        scenario.interest_rate_percentage,
        scenario.loan_term_years,
    )
    expenses = monthly_expenses(
        mortgage_cop=mortgage_cop,
        hoa_monthly_cop=scenario.hoa_monthly_cop,
        annual_revenue_cop=scenario.annual_revenue_cop,
        purchase_price_cop=scenario.purchase_price_cop,
        assessed_value_cop=scenario.assessed_value_cop,
        management_fee_percentage=scenario.management_fee_percentage,
        maintenance_reserve_percentage=scenario.maintenance_reserve_percentage,
        predial_rate_percentage=scenario.predial_rate_percentage,
    )
    net_income_cop = annual_net_income(scenario.annual_revenue_cop, expenses.total_cop)
    invested_cop = cash_invested(
        scenario.purchase_price_cop,
        scenario.down_payment_percentage,
        scenario.closing_costs_percentage,
        scenario.renovation_budget_cop,
    )

    return AnalysisResult(
        cop_per_usd=scenario.cop_per_usd,
        annual_revenue_cop=scenario.annual_revenue_cop,
        monthly_expenses=expenses,
        annual_net_income_cop=net_income_cop,
        cash_invested_cop=invested_cop,
        coc_return_percentage=coc_return(net_income_cop, invested_cop),
        payback_years=payback_period(invested_cop, net_income_cop),
    )


def sensitivity(
    scenario: PropertyScenario,
    factors: tuple[float, ...] = DEFAULT_SENSITIVITY_FACTORS,
) -> list[SensitivityCell]:
    """
    Re-runs the scenario at scaled revenue, one cell per factor.

    A single axis by necessity. Step 12 asks for a 3x3 grid of ADR against
    occupancy, but revenue is ``ADR x occupancy x 365``, so both axes scale the same
    product - the nine cells collapse to six distinct values with the anti-diagonal
    repeating. Three cells along revenue is the whole of the information the grid
    would have carried.

    Each variant is copied from the *original* scenario rather than the previous
    one, so the factors stay independent instead of compounding.
    """
    cells = []

    for factor in factors:
        variant = scenario.model_copy(
            update={"annual_revenue_cop": scenario.annual_revenue_cop * factor}
        )
        result = analyze(variant)
        cells.append(
            SensitivityCell(
                revenue_factor=factor,
                annual_revenue_cop=result.annual_revenue_cop,
                coc_return_percentage=result.coc_return_percentage,
                payback_years=result.payback_years,
            )
        )

    return cells


def conservative_of(*results: AnalysisResult) -> AnalysisResult:
    """
    The least optimistic of several analyses of the same property.

    Step 6 produces two revenue estimates - AirROI's own calculator and a
    comp-derived median - and has to mark one of them conservative. Net income
    decides it rather than CoC return or payback: it is the figure both of those
    derive from, and unlike payback it is never ``None``.

    ``min`` keeps the first of equal candidates, so two identical estimates return
    the one given first rather than an arbitrary pick.
    """
    if not results:
        raise ValueError("conservative_of requires at least one AnalysisResult")

    return min(results, key=lambda result: result.annual_net_income_cop)
