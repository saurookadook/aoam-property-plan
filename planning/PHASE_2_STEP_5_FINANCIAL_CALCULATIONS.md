# Phase 2 / Step 5 — Financial Calculation Module

Implementation plan for `docs/COLOMBIA_STR_EXECUTION_PLAN_v3.md` → Part 3 → Phase 2 → Step 5.

---

## Context

Phase 2 / Step 5 calls for `calculations.py` — the module that turns a purchase price and a
revenue estimate into cash-on-cash return and payback period. Step 4 landed
`POST /api/properties`, so a candidate property now has a real `purchase_price_cop`. Step 6
will supply the revenue side from AirROI comps. Step 5 is the arithmetic in between, and it is
the last piece with no external dependency of its own.

Confirmed greenfield: grepping `mortgage|payback|coc_return|closing_cost|down_payment` across
`backend/` hits only `models/property_financial_report/*`, its factory, and migrations. Nothing
computes anything yet.

**Outcome:** `backend/services/calculations.py` — pure, dependency-free, unit-tested. No DB
session, no HTTP route, no migration.

---

## Verified against the doc

Every figure below was computed and checked before writing this plan.

### The doc's own acceptance figure is wrong

Part 4, row 5 states: *"COP 500M Calima finca at 30% down, 10% rate, 15 years, 0 HOA = ~USD
1,540/month mortgage."* With those exact inputs the answer is **COP 3,761,117.91/month**, which
is **USD 906.29** at 4,150 COP/USD.

```
loan        = 500,000,000 × 0.70 = 350,000,000 COP
r           = 10.0 / 100 / 12    = 0.0083̄
n           = 15 × 12            = 180
payment     = P·r / (1 − (1+r)^−n)
            = 3,761,117.91 COP   →  906.29 USD @ 4,150
```

USD 1,540 is only reachable at **0% down over a 10-year term** (0% / 10yr / 9% → 1,526.21;
0% / 10yr / 10% → 1,592.18). No plausible exchange rate closes the gap at 30% down over 15
years. This plan asserts the correct value and records the discrepancy so the doc gets fixed,
rather than bending the code to match it — the same posture Step 4's plan took with
`postal_code` and the BeautifulSoup assumption.

### The doc's six functions do not close the loop

- `coc_return` and `payback_period` both consume *cash invested*, and nothing computes it.
- **Predial** is defined in Part 6 (0.8%/yr) but is absent from the `monthly_expenses`
  signature in Step 5. Omitting it overstates net income by COP 333,333/month on a 500M
  property.

### The 3×3 sensitivity grid is mathematically degenerate

Step 12 specifies a 3×3 grid of CoC at ADR −10%/base/+10% **vs** occupancy −10%/base/+10%.
Since `revenue = ADR × occupancy × 365`, both axes are the same multiplication on revenue. The
nine cells collapse to six distinct values, and the anti-diagonal repeats by construction:

```
        occ 0.9   occ 1.0   occ 1.1
adr 0.9   0.81      0.90      0.99
adr 1.0   0.90      1.00      1.10     ← 0.90 and 1.10 each appear twice
adr 1.1   0.99      1.10      1.21
```

Step 5 therefore ships a **one-axis revenue multiplier** returning three cells, not nine.
**This is a change Step 12 must absorb** — see Notes.

### Repo conventions confirmed

| Convention | Evidence |
| :--- | :--- |
| Percentages are whole numbers | `models/_tests/conftest.py:150-155` — `coc_return_percentage=10.0`, `down_payment_percentage=20.0`, `interest_rate=5.0` |
| Money is `float`, never `Decimal` | `Mapped[float]` on `NUMERIC` columns; `Decimal` appears only in `models/listing/entity.py:15` for WKT strings |
| `services/` is flat functions, sync, no classes | `services/{exchange_rate,finca_raiz,property_source}.py` |
| Service logger | `logger = cast(ExtendedLogger, logging.getLogger(__name__))` — routes use `init_logging(__file__)`, services do not |
| Tests live beside the code | `services/_tests/test_<module>.py`, one class per public function, sentence-named methods, `pytest.approx`, heavy `parametrize` |
| Packaging | `constants` and `services` are **already** in `[tool.hatch.build.targets.wheel]` — no `pyproject.toml` change needed |

---

## Decisions

| Decision | Choice |
| :--- | :--- |
| Scope | Pure module + unit tests. No DB, no route, no migration. |
| Calculation currency | COP-native throughout |
| Result currency | COP only; `AnalysisResult` carries the `cop_per_usd` it was built with |
| Numeric type | `float`, no rounding inside the module |
| Percentages | Whole numbers (`10.0` = 10%), matching the DB fixtures |
| Math location | Flat pure functions; models bundle inputs only |
| Container type | Frozen Pydantic v2 models |
| Result shape | Calc-native superset of `property_financial_reports` |
| Defaults home | `backend/constants/colombia.py` (new module in the existing package) |
| Predial basis | Separate `assessed_value_cop`, defaulting to purchase price |
| Zero interest rate | `principal / n`, not a division by zero |
| 100% down | Principal 0 → payment `0.0` |
| Non-positive net income | `payback_period` → `None`; `coc_return` → the real negative percentage |
| Invalid inputs | `ValueError` (`term_years <= 0`, `purchase_price_cop <= 0`) |
| Sensitivity | One axis, revenue multipliers `(0.9, 1.0, 1.1)` → three cells |
| Dual revenue estimates | `conservative_of(*results)` helper ships now, for Step 6 |
| `calculated_at` | **Not** stamped here — `analyze()` stays pure; Step 6 stamps on persist |
| Exchange rate | Always an input, sourced from an `exchange_rates` row. Never a constant. |

---

## Implementation

### 1. `backend/constants/colombia.py` (new)

`constants/__init__.py` is a grab-bag (terminal width, `AIRROI_BASE_URL`); do not add to it.
A dedicated module holds Part 6's operating assumptions as the single source of truth, so
Step 8 can later serve them and Step 12 stops hardcoding values that also govern the math:

```python
DEFAULT_INTEREST_RATE_PERCENTAGE       = 10.0
DEFAULT_DOWN_PAYMENT_PERCENTAGE        = 30.0
DEFAULT_LOAN_TERM_YEARS                = 15
DEFAULT_MANAGEMENT_FEE_PERCENTAGE      = 22.0
DEFAULT_MAINTENANCE_RESERVE_PERCENTAGE = 1.0    # of purchase price, per year
DEFAULT_CLOSING_COSTS_PERCENTAGE       = 2.75
DEFAULT_PREDIAL_RATE_PERCENTAGE        = 0.8    # of assessed value, per year
HOA_MONTHLY_COP_BY_CITY = {"Bogota": 500_000, "Medellin": 500_000, "Cali": 300_000}
DEFAULT_HOA_MONTHLY_COP = 0.0   # rural fincas — Calima, Pance, Salento
MONTHS_PER_YEAR = 12
```

Each value carries a comment naming its Part 6 row. `MONTHS_PER_YEAR` lives here too so the
÷12 conversions stop being a bare literal repeated five times.

### 2. Models — top of `services/calculations.py`

Four frozen `BaseModel`s. This is the first Pydantic use inside `services/` (the scrapers hand
dicts to the facades instead); the reason is that Step 8's analyze-request model can derive
from `PropertyScenario` rather than redeclaring nine fields, and `model_copy(update=...)` is
what drives the sensitivity variants.

- **`PropertyScenario`** — `model_config = ConfigDict(frozen=True)`.
  `purchase_price_cop: float = Field(gt=0)`, `annual_revenue_cop: float = Field(ge=0)`,
  `cop_per_usd: float = Field(gt=0)`,
  `assessed_value_cop: Optional[float] = Field(default=None, gt=0)`,
  `hoa_monthly_cop: float = Field(default=0.0, ge=0)`,
  `renovation_budget_cop: float = Field(default=0.0, ge=0)`, plus the six percentage/term
  fields defaulted from `constants.colombia` and bounded (`ge=0, le=100`; term `gt=0`).
  A `@model_validator(mode="after")` resolves `assessed_value_cop` to `purchase_price_cop`
  when unset, so downstream code never branches on `None`.
- **`MonthlyExpenseBreakdown`** — `mortgage_cop`, `hoa_cop`, `management_fee_cop`,
  `maintenance_reserve_cop`, `predial_cop`, and `total_cop`. All COP. `total_cop` is the sum;
  Step 12 renders the lines.
- **`AnalysisResult`** — `cop_per_usd` (echoed from the scenario, so Step 6 has the rate for
  the `_usd` columns and for `property_financial_reports.exchange_rate`),
  `annual_revenue_cop`, `monthly_expenses: MonthlyExpenseBreakdown`,
  `annual_net_income_cop`, `cash_invested_cop`, `coc_return_percentage`,
  `payback_years: Optional[float]`. A superset of the table — the breakdown and the monthly
  mortgage figure have no columns yet, which is fine; Step 6 selects the subset that maps.
- **`SensitivityCell`** — `revenue_factor`, `annual_revenue_cop`, `coc_return_percentage`,
  `payback_years: Optional[float]`.

### 3. Functions — flat, pure, `from __future__ import annotations` on line 1

The doc's six, plus the three it needs and omits:

| Function | Signature | Notes |
| :--- | :--- | :--- |
| `mortgage_payment` | `(principal_cop, annual_rate_percentage, term_years) -> float` | `0` rate → `principal / n`; `principal == 0` → `0.0`; `term_years <= 0` → `ValueError` |
| `annual_predial` | `(assessed_value_cop, predial_rate_percentage=…) -> float` | **new** — closes the Part 6 gap |
| `closing_costs` | `(purchase_price_cop, closing_costs_percentage=2.75) -> float` | |
| `cash_invested` | `(purchase_price_cop, down_payment_percentage, closing_costs_percentage, renovation_budget_cop=0.0) -> float` | **new** — reuses `closing_costs` |
| `monthly_expenses` | `(...) -> MonthlyExpenseBreakdown` | Returns the breakdown, not a bare float. Management fee is 22% of **gross** revenue ÷ 12; maintenance is 1% of purchase price ÷ 12 |
| `annual_net_income` | `(annual_revenue_cop, monthly_expenses_cop) -> float` | `revenue − expenses × 12` |
| `coc_return` | `(annual_net_income_cop, cash_invested_cop) -> float` | Whole-number percentage; returns the real negative on a loss |
| `payback_period` | `(cash_invested_cop, annual_net_income_cop) -> Optional[float]` | `None` when net income ≤ 0 — never negative, never `inf`, both of which read as "pays back fast" and neither of which survives the `NUMERIC` round-trip cleanly |
| `analyze` | `(scenario: PropertyScenario) -> AnalysisResult` | Composition only — no arithmetic of its own |
| `sensitivity` | `(scenario, factors=(0.9, 1.0, 1.1)) -> list[SensitivityCell]` | `analyze(scenario.model_copy(update={"annual_revenue_cop": rev * f}))` per factor |
| `conservative_of` | `(*results: AnalysisResult) -> AnalysisResult` | Lowest `annual_net_income_cop` wins; first on a tie; `ValueError` on empty. Serves Step 6's "mark the lower of the two as conservative" |

Docstrings follow house style — prose explaining *why*, ``double-backtick`` identifiers. The
`payback_period` and `annual_predial` docstrings in particular must state their reasoning,
since both encode a judgement the doc does not.

**Deliberately not here:** no `datetime` (keeps `analyze` pure and sidesteps the autouse
`patch_utcnow` fixture), no DB session, no currency conversion —
`services/exchange_rate.convert_cop_to_usd` already exists and Step 6 calls it.

### 4. Tests — `backend/services/_tests/test_calculations.py`

One class per public function, sentence-named methods, `pytest.approx`, `parametrize` for edge
cases — the template is `TestConvertCopToUsd` in `services/_tests/test_exchange_rate.py:110`.
Pure functions, so no DB fixtures (the root `test_db_session` fixture is autouse and still
wraps each test; harmless).

**`TestMortgagePayment`** — the doc's acceptance case, asserting COP as primary because it is
the only rate-independent figure:

| Case | Expected |
| :--- | :--- |
| `(350_000_000, 10.0, 15)` | `3_761_117.91` COP |
| ÷ `cop_per_usd=4150.0` | `906.29` USD |
| ÷ `cop_per_usd=4400.0` | `854.80` USD — proves the rate is genuinely an input |
| `(350_000_000, 0.0, 15)` | `1_944_444.44` = `350M / 180` |
| `(0.0, 10.0, 15)` (100% down) | `0.0` |
| `term_years=0` | `ValueError` |

Add a test asserting the doc's `~1,540` is **not** produced at 30%/15yr, named so the intent
survives — this is exactly the assertion a future reader is likely to "fix" back to the doc.

**`TestAnalyze`** — one end-to-end worked example, a COP 500M Calima finca at Part 6 defaults
with revenue USD 19,000 (COP 78,850,000 @ 4,150), covering the doc's mid-range Calima estimate:

```
mortgage             3,761,117.91
hoa                          0.00   (rural finca)
management (22%)     1,445,583.33
maintenance (1%/yr)    416,666.67
predial (0.8%/yr)      333,333.33
                    ─────────────
monthly expenses     5,956,701.25

annual net income    7,369,585.06
cash invested      163,750,000.00   (150M down + 13.75M closing)
CoC return                4.5005 %
payback                   22.22 years
```

**`TestSensitivity`** — three cells from the same scenario:

| factor | revenue | CoC | payback |
| :--- | ---: | ---: | ---: |
| 0.9 | 70,965,000 | 0.7446% | 134.30 |
| 1.0 | 78,850,000 | 4.5005% | 22.22 |
| 1.1 | 86,735,000 | 8.2564% | 12.11 |

The spread is the point: a 10% revenue swing moves CoC by ~3.8 points. Assert the ordering is
monotonic, not just the values.

**`TestPaybackPeriod` / `TestCocReturn`** — the loss case (revenue COP 40,000,000):
`annual_net_income == −22,933,414.94`, `coc_return == −14.0051`, `payback_period is None`.
Assert `None` explicitly rather than falsy, so a future `0.0` regression fails.

**`TestPropertyScenario`** — validation boundaries: `purchase_price_cop=0` and
`down_payment_percentage=150` raise `ValidationError`; `assessed_value_cop` unset resolves to
`purchase_price_cop`; set to 60% of price yields predial of exactly 60% the default figure.
Also assert the model is frozen (mutation raises), since the sensitivity path depends on it.

**`TestConservativeOf`** — lower net income wins; identical inputs return the first; empty
raises `ValueError`.

---

## Files

**New**

- `backend/constants/colombia.py`
- `backend/services/calculations.py`
- `backend/services/_tests/test_calculations.py`

**Modified**

- None. `constants` and `services` are already declared in `pyproject.toml`, no dependency is
  added, and no existing module needs to change.

---

## Verification

```sh
docker compose run --rm backend-test pytest services/_tests/test_calculations.py -vvv
docker compose run --rm backend-test pytest services/_tests   # no regressions in Step 4
```

Then confirm the doc's row-5 acceptance criterion by hand, in the same container:

```sh
docker compose run --rm backend-test python -c "
from services.calculations import mortgage_payment
cop = mortgage_payment(350_000_000, 10.0, 15)
print(f'{cop:,.2f} COP  =  {cop/4150:,.2f} USD')"
# 3,761,117.91 COP  =  906.29 USD
```

Lint locally with the settings from `.vscode/settings.json` — there is **no lint step in CI**
(`.github/workflows/backend-test.yml` builds images and runs pytest only), so this is manual:

```sh
flake8 --max-line-length=120 services/calculations.py constants/colombia.py
black --check services/calculations.py constants/colombia.py   # code is 88-col black
```

---

## Notes — carried forward

- **The doc needs two corrections.** Part 4 row 5's `~USD 1,540/month` is unreachable at its
  own stated inputs; the value is USD 906.29 at 4,150 COP/USD. And Step 5's `monthly_expenses`
  signature omits predial, which Part 6 defines.
- **Step 12 must relabel the sensitivity panel.** The specified 3×3 ADR-vs-occupancy grid has
  no second dimension. Three cells along one revenue axis is what the math supports.
- **`property_financial_reports` cannot store the inputs.** No columns for HOA, management fee
  %, maintenance, closing costs, renovation budget, or the monthly mortgage figure. Step 6
  needs a migration to widen it, or those values are recomputed on every read.
- **HOA is already available and unused.** Step 4's scraper writes `common_expenses_cop` into
  `properties.notes` as JSON (`services/finca_raiz.py:206`). Step 6 should read it instead of
  falling back to the Part 6 default whenever the listing supplied a real figure.
- **`calculated_at` is naive.** The column is `postgresql.TIMESTAMP` with no timezone, unlike
  `created_at`/`updated_at` from `TimestampsDB`. Step 6 will hit this; noting it here.
- Debt service is counted in full, principal included. That is standard for cash-on-cash and
  makes the figure deliberately conservative — worth a line in the module docstring so nobody
  later "fixes" it to interest-only.
