from __future__ import annotations

import pytest
from pydantic import ValidationError

from services import calculations as calculations_service
from services.calculations import PropertyScenario

# The doc's mid-range Calima estimate: a COP 500M finca earning USD 19,000/year at
# 4,150 COP/USD, on Part 6's defaults. Every worked figure below traces back to it.
CALIMA_PURCHASE_PRICE_COP = 500_000_000.0
CALIMA_ANNUAL_REVENUE_COP = 78_850_000.0
COP_PER_USD = 4150.0

# 30% down on COP 500M.
CALIMA_LOAN_PRINCIPAL_COP = 350_000_000.0

# 150M down + 13.75M closing, no renovation.
CALIMA_CASH_INVESTED_COP = 163_750_000.0


@pytest.fixture
def calima_scenario() -> PropertyScenario:
    return PropertyScenario(
        purchase_price_cop=CALIMA_PURCHASE_PRICE_COP,
        annual_revenue_cop=CALIMA_ANNUAL_REVENUE_COP,
        cop_per_usd=COP_PER_USD,
    )


class TestLoanPrincipal:
    def test_borrows_what_the_down_payment_does_not_cover(self):
        assert calculations_service.loan_principal(
            CALIMA_PURCHASE_PRICE_COP, 30.0
        ) == pytest.approx(CALIMA_LOAN_PRINCIPAL_COP)

    def test_borrows_nothing_when_the_buyer_pays_in_full(self):
        assert calculations_service.loan_principal(
            CALIMA_PURCHASE_PRICE_COP, 100.0
        ) == pytest.approx(0.0)

    def test_borrows_the_whole_price_with_no_down_payment(self):
        assert calculations_service.loan_principal(
            CALIMA_PURCHASE_PRICE_COP, 0.0
        ) == pytest.approx(CALIMA_PURCHASE_PRICE_COP)

    @pytest.mark.parametrize("purchase_price_cop", [0.0, -1.0])
    def test_rejects_a_non_positive_purchase_price(self, purchase_price_cop):
        with pytest.raises(ValueError):
            calculations_service.loan_principal(purchase_price_cop, 30.0)


class TestMortgagePayment:
    def test_amortises_the_principal_over_the_term(self):
        """
        The doc's Part 4 row 5 acceptance case. Asserted in COP because that is the
        only figure independent of whatever exchange rate happens to apply.
        """
        assert calculations_service.mortgage_payment(
            CALIMA_LOAN_PRINCIPAL_COP, 10.0, 15
        ) == pytest.approx(3_761_117.91, abs=0.01)

    @pytest.mark.parametrize(
        "cop_per_usd, expected_usd",
        [
            (4150.0, 906.29),
            (4400.0, 854.80),
        ],
    )
    def test_converts_to_usd_at_whatever_rate_is_supplied(
        self, cop_per_usd, expected_usd
    ):
        """Two rates, two answers - proof the rate is an input and not a constant."""
        payment_cop = calculations_service.mortgage_payment(
            CALIMA_LOAN_PRINCIPAL_COP, 10.0, 15
        )

        assert payment_cop / cop_per_usd == pytest.approx(expected_usd, abs=0.01)

    def test_does_not_produce_the_figure_the_doc_claims(self):
        """
        Part 4 row 5 asserts ~USD 1,540/month at 30% down over 15 years at 10%. It
        is not reachable: the correct answer is USD 906.29 at 4,150 COP/USD, and no
        plausible rate closes a 70% gap.

        This test exists because the discrepancy looks like a bug in the code rather
        than in the doc, and is exactly the kind of thing a future reader "fixes"
        back. The doc is what needs correcting.
        """
        payment_usd = (
            calculations_service.mortgage_payment(CALIMA_LOAN_PRINCIPAL_COP, 10.0, 15)
            / COP_PER_USD
        )

        assert payment_usd == pytest.approx(906.29, abs=0.01)
        assert payment_usd != pytest.approx(1540.0, abs=1.0)

    def test_spreads_the_principal_evenly_at_a_zero_interest_rate(self):
        """No interest means no annuity - just the principal over 180 months."""
        assert calculations_service.mortgage_payment(
            CALIMA_LOAN_PRINCIPAL_COP, 0.0, 15
        ) == pytest.approx(CALIMA_LOAN_PRINCIPAL_COP / 180)

    def test_costs_nothing_when_there_is_no_loan(self):
        assert calculations_service.mortgage_payment(0.0, 10.0, 15) == 0.0

    @pytest.mark.parametrize("term_years", [0, -5])
    def test_rejects_a_non_positive_term(self, term_years):
        with pytest.raises(ValueError):
            calculations_service.mortgage_payment(
                CALIMA_LOAN_PRINCIPAL_COP, 10.0, term_years
            )

    def test_rejects_a_negative_principal(self):
        with pytest.raises(ValueError):
            calculations_service.mortgage_payment(-1.0, 10.0, 15)


class TestAnnualPredial:
    def test_charges_the_rate_against_the_assessed_value(self):
        assert calculations_service.annual_predial(
            CALIMA_PURCHASE_PRICE_COP, 0.8
        ) == pytest.approx(4_000_000.0)

    def test_follows_the_assessed_value_rather_than_the_purchase_price(self):
        """
        Predial is levied on the cadastral value, which in Colombia sits below the
        sale price - so a lower assessed value has to produce a lower bill.
        """
        assert calculations_service.annual_predial(300_000_000.0, 0.8) == pytest.approx(
            2_400_000.0
        )


class TestClosingCosts:
    def test_charges_the_colombian_default_of_2_75_percent(self):
        assert calculations_service.closing_costs(
            CALIMA_PURCHASE_PRICE_COP
        ) == pytest.approx(13_750_000.0)

    @pytest.mark.parametrize("purchase_price_cop", [0.0, -1.0])
    def test_rejects_a_non_positive_purchase_price(self, purchase_price_cop):
        with pytest.raises(ValueError):
            calculations_service.closing_costs(purchase_price_cop)


class TestCashInvested:
    def test_sums_the_down_payment_and_the_closing_costs(self):
        assert calculations_service.cash_invested(
            CALIMA_PURCHASE_PRICE_COP, 30.0, 2.75
        ) == pytest.approx(CALIMA_CASH_INVESTED_COP)

    def test_includes_the_renovation_budget(self):
        assert calculations_service.cash_invested(
            CALIMA_PURCHASE_PRICE_COP, 30.0, 2.75, 20_000_000.0
        ) == pytest.approx(CALIMA_CASH_INVESTED_COP + 20_000_000.0)

    def test_counts_the_whole_price_when_nothing_is_borrowed(self):
        assert calculations_service.cash_invested(
            CALIMA_PURCHASE_PRICE_COP, 100.0, 2.75
        ) == pytest.approx(513_750_000.0)


class TestMonthlyExpenses:
    @pytest.fixture
    def calima_expenses(self):
        return calculations_service.monthly_expenses(
            mortgage_cop=3_761_117.91,
            hoa_monthly_cop=0.0,
            annual_revenue_cop=CALIMA_ANNUAL_REVENUE_COP,
            purchase_price_cop=CALIMA_PURCHASE_PRICE_COP,
        )

    @pytest.mark.parametrize(
        "line, expected_cop",
        [
            ("mortgage_cop", 3_761_117.91),
            ("hoa_cop", 0.0),
            ("management_fee_cop", 1_445_583.33),
            ("maintenance_reserve_cop", 416_666.67),
            ("predial_cop", 333_333.33),
            ("total_cop", 5_956_701.25),
        ],
    )
    def test_itemises_every_line(self, calima_expenses, line, expected_cop):
        assert getattr(calima_expenses, line) == pytest.approx(expected_cop, abs=0.01)

    def test_totals_its_own_lines(self, calima_expenses):
        assert calima_expenses.total_cop == pytest.approx(
            calima_expenses.mortgage_cop
            + calima_expenses.hoa_cop
            + calima_expenses.management_fee_cop
            + calima_expenses.maintenance_reserve_cop
            + calima_expenses.predial_cop
        )

    def test_charges_the_management_fee_on_gross_revenue(self):
        """22% of gross, not of net - which is how Colombian STR managers bill."""
        expenses = calculations_service.monthly_expenses(
            mortgage_cop=0.0,
            annual_revenue_cop=12_000_000.0,
            purchase_price_cop=CALIMA_PURCHASE_PRICE_COP,
            management_fee_percentage=22.0,
        )

        assert expenses.management_fee_cop == pytest.approx(220_000.0)

    def test_charges_predial_even_though_the_doc_omits_it(self):
        """
        Part 6 defines predial but Step 5's expense list leaves it out. On a COP
        500M property the omission overstates monthly net income by COP 333,333.
        """
        expenses = calculations_service.monthly_expenses(
            mortgage_cop=0.0,
            annual_revenue_cop=CALIMA_ANNUAL_REVENUE_COP,
            purchase_price_cop=CALIMA_PURCHASE_PRICE_COP,
        )

        assert expenses.predial_cop == pytest.approx(333_333.33, abs=0.01)

    def test_defaults_the_predial_basis_to_the_purchase_price(self):
        without_assessed_value = calculations_service.monthly_expenses(
            mortgage_cop=0.0,
            annual_revenue_cop=CALIMA_ANNUAL_REVENUE_COP,
            purchase_price_cop=CALIMA_PURCHASE_PRICE_COP,
        )
        with_assessed_value = calculations_service.monthly_expenses(
            mortgage_cop=0.0,
            annual_revenue_cop=CALIMA_ANNUAL_REVENUE_COP,
            purchase_price_cop=CALIMA_PURCHASE_PRICE_COP,
            assessed_value_cop=CALIMA_PURCHASE_PRICE_COP,
        )

        assert without_assessed_value.predial_cop == pytest.approx(
            with_assessed_value.predial_cop
        )

    def test_is_frozen(self, calima_expenses):
        with pytest.raises(ValidationError):
            calima_expenses.mortgage_cop = 0.0


class TestAnnualNetIncome:
    def test_takes_a_full_year_of_expenses_off_revenue(self):
        assert calculations_service.annual_net_income(
            CALIMA_ANNUAL_REVENUE_COP, 5_956_701.245311745
        ) == pytest.approx(7_369_585.06, abs=0.01)

    def test_goes_negative_when_expenses_outrun_revenue(self):
        assert calculations_service.annual_net_income(
            40_000_000.0, 5_244_451.24
        ) == pytest.approx(-22_933_414.88, abs=0.01)


class TestCocReturn:
    def test_expresses_the_return_as_a_whole_number_percentage(self):
        assert calculations_service.coc_return(
            7_369_585.056259051, CALIMA_CASH_INVESTED_COP
        ) == pytest.approx(4.5005, abs=0.0001)

    def test_reports_the_real_negative_on_a_loss(self):
        """
        Not floored at zero: "-14%" and "0%" call for very different decisions.
        """
        assert calculations_service.coc_return(
            -22_933_414.94374095, CALIMA_CASH_INVESTED_COP
        ) == pytest.approx(-14.0051, abs=0.0001)

    @pytest.mark.parametrize("cash_invested_cop", [0.0, -1.0])
    def test_rejects_a_non_positive_cash_investment(self, cash_invested_cop):
        """A return on nothing is not a percentage, however good the deal looks."""
        with pytest.raises(ValueError):
            calculations_service.coc_return(7_369_585.06, cash_invested_cop)


class TestPaybackPeriod:
    def test_divides_the_investment_by_annual_net_income(self):
        assert calculations_service.payback_period(
            CALIMA_CASH_INVESTED_COP, 7_369_585.056259051
        ) == pytest.approx(22.22, abs=0.01)

    @pytest.mark.parametrize("annual_net_income_cop", [-22_933_414.94374095, 0.0])
    def test_never_pays_back_without_positive_net_income(self, annual_net_income_cop):
        """
        Asserted as ``is None`` rather than falsy so that a regression to ``0.0``
        fails here. A negative or infinite payback would sort as though the property
        repaid itself fastest, which is the opposite of the truth.
        """
        result = calculations_service.payback_period(
            CALIMA_CASH_INVESTED_COP, annual_net_income_cop
        )

        assert result is None


class TestAnalyze:
    @pytest.fixture
    def result(self, calima_scenario):
        return calculations_service.analyze(calima_scenario)

    @pytest.mark.parametrize(
        "line, expected_cop",
        [
            ("mortgage_cop", 3_761_117.91),
            ("hoa_cop", 0.0),
            ("management_fee_cop", 1_445_583.33),
            ("maintenance_reserve_cop", 416_666.67),
            ("predial_cop", 333_333.33),
            ("total_cop", 5_956_701.25),
        ],
    )
    def test_breaks_the_monthly_expenses_down(self, result, line, expected_cop):
        assert getattr(result.monthly_expenses, line) == pytest.approx(
            expected_cop, abs=0.01
        )

    @pytest.mark.parametrize(
        "field, expected",
        [
            ("annual_revenue_cop", CALIMA_ANNUAL_REVENUE_COP),
            ("annual_net_income_cop", 7_369_585.06),
            ("cash_invested_cop", CALIMA_CASH_INVESTED_COP),
            ("coc_return_percentage", 4.5005),
            ("payback_years", 22.2197),
        ],
    )
    def test_produces_the_worked_calima_figures(self, result, field, expected):
        assert getattr(result, field) == pytest.approx(expected, abs=0.01)

    def test_echoes_the_exchange_rate_it_was_given(self, result):
        """
        Step 6 fills the ``_usd`` columns and ``exchange_rate`` from this, rather
        than re-resolving a rate that may have moved since.
        """
        assert result.cop_per_usd == COP_PER_USD

    def test_leaves_the_scenario_untouched(self, calima_scenario, result):
        assert calima_scenario.annual_revenue_cop == CALIMA_ANNUAL_REVENUE_COP

    def test_charges_hoa_when_the_property_has_it(self):
        """
        The rural-finca default is zero; an urban apartment is COP 500K/month in
        Bogota, and it has to land on the total.
        """
        urban = PropertyScenario(
            purchase_price_cop=CALIMA_PURCHASE_PRICE_COP,
            annual_revenue_cop=CALIMA_ANNUAL_REVENUE_COP,
            cop_per_usd=COP_PER_USD,
            hoa_monthly_cop=500_000.0,
        )

        result = calculations_service.analyze(urban)

        assert result.monthly_expenses.hoa_cop == pytest.approx(500_000.0)
        assert result.monthly_expenses.total_cop == pytest.approx(
            6_456_701.25, abs=0.01
        )

    def test_reports_a_loss_without_a_payback(self):
        losing = PropertyScenario(
            purchase_price_cop=CALIMA_PURCHASE_PRICE_COP,
            annual_revenue_cop=40_000_000.0,
            cop_per_usd=COP_PER_USD,
        )

        result = calculations_service.analyze(losing)

        assert result.annual_net_income_cop == pytest.approx(-22_933_414.94, abs=0.01)
        assert result.coc_return_percentage == pytest.approx(-14.0051, abs=0.0001)
        assert result.payback_years is None

    def test_costs_no_mortgage_on_a_cash_purchase(self):
        cash_purchase = PropertyScenario(
            purchase_price_cop=CALIMA_PURCHASE_PRICE_COP,
            annual_revenue_cop=CALIMA_ANNUAL_REVENUE_COP,
            cop_per_usd=COP_PER_USD,
            down_payment_percentage=100.0,
        )

        result = calculations_service.analyze(cash_purchase)

        assert result.monthly_expenses.mortgage_cop == 0.0
        assert result.cash_invested_cop == pytest.approx(513_750_000.0)

    def test_is_frozen(self, result):
        with pytest.raises(ValidationError):
            result.coc_return_percentage = 99.0


class TestSensitivity:
    @pytest.fixture
    def cells(self, calima_scenario):
        return calculations_service.sensitivity(calima_scenario)

    def test_returns_one_cell_per_factor(self, cells):
        """
        Three cells, not the doc's nine. ``revenue = ADR x occupancy x 365``, so an
        ADR-by-occupancy grid scales the same product on both axes and repeats its
        own values along the anti-diagonal.
        """
        assert len(cells) == 3
        assert [cell.revenue_factor for cell in cells] == [0.9, 1.0, 1.1]

    @pytest.mark.parametrize(
        "index, annual_revenue_cop, coc_return_percentage, payback_years",
        [
            (0, 70_965_000.0, 0.7446, 134.30),
            (1, 78_850_000.0, 4.5005, 22.22),
            (2, 86_735_000.0, 8.2564, 12.11),
        ],
    )
    def test_scales_revenue_by_each_factor(
        self, cells, index, annual_revenue_cop, coc_return_percentage, payback_years
    ):
        cell = cells[index]

        assert cell.annual_revenue_cop == pytest.approx(annual_revenue_cop)
        assert cell.coc_return_percentage == pytest.approx(
            coc_return_percentage, abs=0.0001
        )
        assert cell.payback_years == pytest.approx(payback_years, abs=0.01)

    def test_returns_rise_with_revenue(self, cells):
        """
        The spread is the point of the panel: a 10% revenue swing moves CoC by
        roughly 3.8 points either way, which is what makes the estimate worth
        questioning. Ordering is asserted as well as the values so that a sign error
        cannot pass by matching three numbers in the wrong order.
        """
        returns = [cell.coc_return_percentage for cell in cells]
        paybacks = [cell.payback_years for cell in cells]

        assert returns == sorted(returns)
        assert paybacks == sorted(paybacks, reverse=True)

    def test_accepts_a_different_set_of_factors(self, calima_scenario):
        cells = calculations_service.sensitivity(calima_scenario, factors=(1.0,))

        assert len(cells) == 1
        assert cells[0].annual_revenue_cop == pytest.approx(CALIMA_ANNUAL_REVENUE_COP)

    def test_varies_each_cell_from_the_original_scenario(self, calima_scenario):
        """Factors stay independent instead of compounding down the list."""
        cells = calculations_service.sensitivity(calima_scenario, factors=(0.5, 0.5))

        assert cells[0].annual_revenue_cop == pytest.approx(cells[1].annual_revenue_cop)


class TestConservativeOf:
    @pytest.fixture
    def comp_derived(self, calima_scenario):
        return calculations_service.analyze(calima_scenario)

    @pytest.fixture
    def airroi_estimate(self, calima_scenario):
        return calculations_service.analyze(
            calima_scenario.model_copy(update={"annual_revenue_cop": 60_000_000.0})
        )

    def test_picks_the_lower_net_income(self, comp_derived, airroi_estimate):
        """
        Step 6 surfaces two revenue estimates and marks the lower one conservative.
        """
        result = calculations_service.conservative_of(comp_derived, airroi_estimate)

        assert result is airroi_estimate

    def test_does_not_depend_on_the_order_given(self, comp_derived, airroi_estimate):
        result = calculations_service.conservative_of(airroi_estimate, comp_derived)

        assert result is airroi_estimate

    def test_keeps_the_first_of_two_identical_estimates(self, calima_scenario):
        first = calculations_service.analyze(calima_scenario)
        second = calculations_service.analyze(calima_scenario)

        assert calculations_service.conservative_of(first, second) is first

    def test_returns_a_lone_result_unchanged(self, comp_derived):
        assert calculations_service.conservative_of(comp_derived) is comp_derived

    def test_rejects_an_empty_set_of_results(self):
        with pytest.raises(ValueError):
            calculations_service.conservative_of()


class TestPropertyScenario:
    def test_defaults_to_the_part_6_assumptions(self, calima_scenario):
        assert calima_scenario.down_payment_percentage == 30.0
        assert calima_scenario.interest_rate_percentage == 10.0
        assert calima_scenario.loan_term_years == 15
        assert calima_scenario.management_fee_percentage == 22.0
        assert calima_scenario.maintenance_reserve_percentage == 1.0
        assert calima_scenario.closing_costs_percentage == 2.75
        assert calima_scenario.predial_rate_percentage == 0.8
        assert calima_scenario.hoa_monthly_cop == 0.0
        assert calima_scenario.renovation_budget_cop == 0.0

    def test_assumes_the_purchase_price_is_the_assessed_value(self, calima_scenario):
        assert calima_scenario.assessed_value_cop == CALIMA_PURCHASE_PRICE_COP

    def test_keeps_an_assessed_value_that_was_supplied(self):
        scenario = PropertyScenario(
            purchase_price_cop=CALIMA_PURCHASE_PRICE_COP,
            annual_revenue_cop=CALIMA_ANNUAL_REVENUE_COP,
            cop_per_usd=COP_PER_USD,
            assessed_value_cop=300_000_000.0,
        )

        assert scenario.assessed_value_cop == 300_000_000.0

    def test_a_lower_assessed_value_lowers_predial_proportionally(
        self, calima_scenario
    ):
        """
        60% of the purchase price as the cadastral value has to produce exactly 60%
        of the predial bill - the tax follows the assessed value, not the price.
        """
        discounted = calculations_service.analyze(
            calima_scenario.model_copy(
                update={"assessed_value_cop": CALIMA_PURCHASE_PRICE_COP * 0.6}
            )
        )
        full = calculations_service.analyze(calima_scenario)

        assert discounted.monthly_expenses.predial_cop == pytest.approx(
            full.monthly_expenses.predial_cop * 0.6
        )

    def test_is_frozen(self, calima_scenario):
        """
        The sensitivity sweep rebuilds scenarios through ``model_copy``; a mutable
        scenario would let one variant's edit leak into the next.
        """
        with pytest.raises(ValidationError):
            calima_scenario.annual_revenue_cop = 1.0

    @pytest.mark.parametrize(
        "overrides",
        [
            {"purchase_price_cop": 0.0},
            {"purchase_price_cop": -1.0},
            {"annual_revenue_cop": -1.0},
            {"cop_per_usd": 0.0},
            {"assessed_value_cop": 0.0},
            {"down_payment_percentage": 150.0},
            {"down_payment_percentage": -1.0},
            {"interest_rate_percentage": -1.0},
            {"loan_term_years": 0},
            {"management_fee_percentage": 101.0},
            {"hoa_monthly_cop": -1.0},
            {"renovation_budget_cop": -1.0},
        ],
    )
    def test_rejects_an_impossible_input(self, overrides):
        with pytest.raises(ValidationError):
            PropertyScenario(
                **{
                    "purchase_price_cop": CALIMA_PURCHASE_PRICE_COP,
                    "annual_revenue_cop": CALIMA_ANNUAL_REVENUE_COP,
                    "cop_per_usd": COP_PER_USD,
                    **overrides,
                }
            )

    @pytest.mark.parametrize(
        "overrides",
        [
            {"down_payment_percentage": 100.0},
            {"down_payment_percentage": 0.0},
            {"interest_rate_percentage": 0.0},
            {"annual_revenue_cop": 0.0},
        ],
    )
    def test_accepts_the_legitimate_extremes(self, overrides):
        """
        100% down is a cash purchase, 0% down is full financing, and a 0% rate is
        seller financing - none of them are errors.
        """
        scenario = PropertyScenario(
            **{
                "purchase_price_cop": CALIMA_PURCHASE_PRICE_COP,
                "annual_revenue_cop": CALIMA_ANNUAL_REVENUE_COP,
                "cop_per_usd": COP_PER_USD,
                **overrides,
            }
        )

        assert scenario.purchase_price_cop == CALIMA_PURCHASE_PRICE_COP
