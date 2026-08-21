# Phase 4 — React + TypeScript Dashboard: the missing pieces

Implementation plan for `docs/COLOMBIA_STR_EXECUTION_PLAN_v3.md` → Part 3 → Phase 4 (Steps 10–14).

---

## Context

Phase 4 is the dashboard for evaluating the target markets and individual candidate properties.
The backend built across Phases 1–3 is well ahead of the doc's assumptions — `POST /api/properties`,
`POST /api/properties/{id}/analyze`, `GET /api/properties/{id}/comps` and `/comps/cached` all
exist and produce a rich `PropertyFinancialReportEntity` with revenue percentiles, a 12-month
revenue distribution, peak months, comp counts and COP/USD pairs.

**No frontend consumes any of it.** The React app today is a markets/listings *browser*:
`/home` carousels, `/markets`, `/markets/:marketId`, `/listings/:listingId`. There is no property
concept, no form component anywhere in `src/`, no chart, no currency toggle, and no `useMutation`
in the entire codebase. Measured against the doc's Step 10–13 feature list, **two items are
partially present and nine are absent**.

Everything already built is kept. Every change below is additive, or amends an existing route in
a way that preserves its current response when new parameters are omitted.

**Prerequisite:** this work stacks on `feat/implement-phase2-step6-parts7-8`, which is unmerged
(9 commits ahead of `main`). Phase 4 depends on `services/property_analysis.py` and the
property routes that land with it.

---

## What the data actually says

Everything in this section was computed from files in the repo, not assumed.

### The doc's market numbers are fiction

Computed from `backend/scripts/db/seeding/seed_data/*.json` at COP 4,000/USD:

| Market | ADR (USD) | Occupancy | Annual revenue (USD) | Listings | Doc's Part 1 claim |
| :--- | ---: | ---: | ---: | ---: | :--- |
| Calima | **$215.0** | **0.18** | $7,968 | 177.3 | $65–120 · 55–70% · $16–22K |
| Pance | $99.4 | 0.33 | $6,977 | **27.8** | $60–95 · 55–65% · $13.5–18K |
| Salento | $84.1 | 0.34 | $6,455 | 514.8 | $55–75 · 60–70% · $14.6–19.2K |
| Bogota | $47.3 | 0.40 | $4,218 | 6,375.8 | $34–73 · 53–60% · $9.2–14.6K |

Every market misses the doc's revenue floor by 40–60%. Calima's occupancy is a third of the
claim while its ADR is nearly double it. **Any fit score anchored to Part 1's ranges clamps every
market to zero and ranks nothing.** Pance's 27.8 listings is below the doc's own Step 1
"fewer than 30 → fall back" threshold. Note also that `revenue` is *not* `adr × occupancy × 365`
(Salento: 25.8M actual vs 40.5M formula), so revenue and ADR are genuinely independent signals.

### Nine findings that constrain what Phase 4 can be

**1. Only 4 of the 8 markets are seeded.** `seed_data/` holds Salento, Calima, Pance and Bogota.
Cartagena, Medellín, Santa Marta and Cali have none.

**2. AirROI has no "Granada" and no "El Peñón".** Verified in
`_research/markets/search/{granada,el-penon}_*.json` — **both resolve to `Cali`** (4,690 listings).
The roster must carry Cali standing for the Granada/El Peñón thesis. Do not seed localities
AirROI will not match; `airroi._market_body` sends a three-part tuple and a miss returns nothing.

**3. `properties` has no `market_id`.** `backend/models/property/db.py` carries `city`, `state`
and `neighborhood` as free text scraped from Finca Raiz. `markets` carries AirROI's `locality` —
`"Bogota Capital District - Municipality"`, `"Calima"`, `"Pance"`. A scraped Pance cabin will say
`city: "Cali"`. **They will not match, so the budget indicator has no join key.**

**4. Markets have no coordinates.** `MarketEntity` is four geographic strings. The Colombia map
has nothing to plot. `_market_centroid()` at `api/crons/handlers.py:317` averages a market's
listing coordinates but is a private cron helper — not persisted, not served.

**5. `market_financial_reports.adr_usd` and `.annual_revenue_usd` are written by nothing.**
Verified across every writer (`crons/handlers.py`, `seed_markets.py`). **Always NULL.** Any USD
figure on a market card must be converted client-side from the COP column.

**6. The doc's 3×3 sensitivity grid is mathematically empty**, and `services/calculations.py:466`
already says so: revenue is `ADR × occupancy × 365`, so both axes scale the same product and the
nine cells collapse to six values with a repeating anti-diagonal. `sensitivity()` returns a
3-cell revenue sweep and is **called from nowhere** — dead code awaiting Phase 4.

**7. `market_financial_reports` is populated but served by no route**, and it has no
`monthly_revenue_distribution` column — `handle_markets_peak_months` fetches the distribution and
throws away everything but the top three month names.

**8. CI runs `pnpm test:cov` and nothing else.** `.github/workflows/frontend-test.yml` has no
`pnpm lint` and no `pnpm build:types`. **TypeScript errors cannot fail a PR today**, which makes
"strict for new code" decorative unless a typecheck step is added.

**9. `MonthlyExpenseBreakdown` is never persisted.** `_report_payload` stores the
`monthly_expenses_cop` total and `monthly_mortgage_cop` only. The five expense lines exist solely
on the in-memory `AnalysisResult` — and they are exactly what Step 12's expense card renders.

---

## Decisions taken

| # | Decision |
| :--- | :--- |
| 1 | Scope is frontend **plus** the backend changes it depends on, **plus** a pre-step auditing market coverage and ingestion. |
| 2 | The repo's stack wins over the doc's library list. No recharts, no axios, no `react-router-dom`. Zero new dependencies. |
| 3 | Budget indicator derives a median from scraped `properties`; **hidden below n ≥ 3** with a "Not enough price data (N)" message. |
| 4 | Sensitivity surfaces the backend's existing **3-cell revenue sweep**, not a 3×3 grid, and not recomputed in TypeScript. |
| 5 | Comp table columns come from a **nested `listing` object added to `PropertyCompEntity`** on both comps routes. |
| 6 | TypeScript `strict` for **new Phase 4 files only**. The global flag is not flipped in this plan. |
| 7 | Property IA is a **persistent `/properties` section** (list, new, detail), not a one-shot `/analyze` screen. |
| 8 | Investment fit score is **frontend-computed** from served market metrics with an explicit documented formula. |
| 9 | Step 14 deploy is **already done** via Railway + Caddy. Only the CORS gap and the `VITE_` env documentation are fixed. |
| 10 | `GET /api/markets/{market_id}` gains **optional** query params. |
| 11 | `GET /api/exchange-rate` is added. |
| 12 | Tests for logic, Mirage-backed page tests for new routes, Storybook stories for presentational components. Not test-per-file. |

### Deliberate departures from the doc

- **`recharts` → plain SVG.** No new chart library. See Chunk 6.
- **`axios` → `fetchy`** plus a new `unwrapEnvelope` (see Chunk 4 — `fetchy` currently swallows
  non-2xx responses).
- **`/analyze` one-shot → `/properties` section.** The backend persists properties and reports;
  a write-only screen would discard records the database is keeping and leave `/comps/cached` —
  built specifically to avoid repeat AirROI spend — unreachable.
- **3×3 sensitivity → 3-cell revenue sweep.** Per `calculations.py:466`.
- **Vercel → Railway + Caddy.** `frontend/Dockerfile.release` and `frontend/Caddyfile` already
  deploy the frontend. There is no `vercel.json` and no reason to add one.
- **8 markets → Bogota · Cali · Calima · Pance · Salento · Cartagena · Medellín · Santa Marta**,
  with Cali carrying a display note. Per finding 2.

---

## Chunk breakdown

Seven PRs, matching the repo's one-step-per-PR history (`#27`, `#28`, `#29`, `#33`–`#35`).

| # | Title | Side | Depends on |
| :--- | :--- | :--- | :--- |
| 1 | Market data audit — roster, seed, ingest, `market_id`, centroid | backend | — |
| 2 | Market reads: markets list join, overview params, `/exchange-rate` | backend | 1 |
| 3 | Property reads: list, detail, report, comps with listing, sensitivity | backend | — |
| 4 | Frontend foundation: types, `unwrapEnvelope`, currency, mock plumbing, CI typecheck | frontend | 2 |
| 5 | Step 11 — market overview screen | frontend | 2, 4 |
| 6 | Steps 12–13 — property IA, form, deep-dive, comps | frontend | 3, 4 |
| 7 | Step 14 — CORS + `VITE_API_SERVER_DOMAIN` documentation | both | — |

Chunks 1 and 3 are independent and can start in parallel.

---

## Chunk 1 — Market data audit and roster (backend)

The pre-step. Nothing downstream is worth building until every market has a report.

**Audit first**, pasting the results into this document:

```sql
SELECT m.locality, m.region, mfr.adr_cop, mfr.occupancy_rate,
       mfr.annual_revenue_cop, mfr.listing_count, mfr.peak_months, mfr.last_updated
FROM markets m LEFT JOIN LATERAL (
  SELECT * FROM market_financial_reports r
  WHERE r.market_id = m.id ORDER BY r.last_updated DESC LIMIT 1
) mfr ON true ORDER BY m.locality;
```

**Then, in order:**

1. **Capture four new market summaries live** from AirROI and commit the raw responses to
   `_research/markets/summary/`, matching how Salento/Calima/Pance got there. Then add
   `cali_valle-de-cauca_colombia__summary.json`, `cartagena_bolivar_colombia__summary.json`,
   `medellin_antioquia_colombia__summary.json`, `santa-marta_magdalena_colombia__summary.json`
   to `seed_data/`.
2. **Fix `seed_markets.py`** — it `continue`s when a report already exists, so re-running never
   refreshes figures. Update the existing report instead. A seed script that only works once on a
   clean database is not a seed script.
3. **Persist the monthly distribution.** Add `monthly_revenue_distribution REAL[]` to
   `market_financial_reports` (one migration, mirroring the column on
   `property_financial_reports`) and have `handle_markets_peak_months` store what it already
   fetches. Without this a market-level seasonality view is impossible.
4. **Add `market_id` (nullable FK) to `properties`**, resolved at create time by nearest market
   centroid. `services/geo.haversine_km` and the centroid logic already exist, so this is a
   migration plus roughly twenty lines. **This unblocks the budget indicator** (finding 3).
5. **Market centroid on the read path** as `AVG(listings.latitude)` / `AVG(listings.longitude)`
   computed in the query — *not* as columns. It is derived data that changes with every listings
   ingest; reuse `_market_centroid`'s averaging rule so the map marker and the peak-months
   estimate stand on the same point.
6. **`seed_properties.py`**, beside `seed_markets.py`, with at least three real Finca Raiz listing
   URLs per market. See Problem 2 — without it the budget indicator ships permanently empty.
7. Run `manual_run` for `markets_summaries` → `listings_by_market` → `markets_peak_months` in that
   order (peak months needs both), and paste the audit query output again as acceptance evidence.

Leave `adr_usd` / `annual_revenue_usd` NULL and mark them for a later drop — see the currency
rule in Chunk 6.

**Files:** 4 new seed JSON + 4 new `_research/markets/summary/*.json`; two migrations
(`monthly_revenue_distribution`, `properties.market_id`); modified
`models/market_financial_report/{db,entity}.py`, `models/property/{db,entity}.py`,
`api/crons/handlers.py`, `api/routes/handlers/properties.py`,
`scripts/db/seeding/seed_markets.py`, new `scripts/db/seeding/seed_properties.py`,
`_factories/`, `models/_tests/conftest.py`.

---

## Chunk 2 — Market reads (backend)

**`GET /api/markets` — nested `financial_report`.** Do *not* widen `MarketEntity`: it is returned
by `/markets/{id}` and consumed by three cron handlers, all of which would then have to supply a
report. Add a read-shaped composite in `models/market/entity.py`, where
`HighestEarningListingEntity` sets the precedent:

```python
class MarketWithFinancialReportEntity(MarketEntity):
    financial_report: Optional[MarketFinancialReportEntity] = None
    latitude: Optional[float] = None   # AVG over the market's listings
    longitude: Optional[float] = None
```

`MarketsListResponse.data` becomes `list[MarketWithFinancialReportEntity]`. Additive — the four
existing keys are unchanged.

Add `MarketFacade.get_all_with_latest_reports()` using a single
`LEFT JOIN LATERAL (… ORDER BY last_updated DESC LIMIT 1)` plus the centroid `AVG`s. Calling
`get_latest_by_market_id` in a loop is 8 extra round trips today and more as the roster grows.

A separate `/api/markets/financial-reports` endpoint was considered and rejected: a market card is
meaningless with half the data, so the halves should not arrive in two responses the client has
to zip by `market_id`.

**`GET /api/markets/{market_id}` — query params.** `bedrooms`, `property_type`,
`sort` (`revenue` | `occupancy`), `limit` (`le=200`). Push all four into
`ListingFacade.get_all_by_market_id(...)` — filtering in Python after fetching every listing
defeats the point of `limit`.

Two honesty notes:

- "Omitting params preserves today's exact behaviour" is **not literally achievable**.
  `get_all_by_market_id` has no `ORDER BY`, so today's order is whatever Postgres returns. Add a
  deterministic `ORDER BY airroi_id ASC` default and call the behaviour change out in the PR.
- `sort=revenue` orders on `listing_financial_reports.ttm_revenue`, a child table with potentially
  several rows per listing. Use the same `LATERAL … LIMIT 1` shape, not a plain join that
  multiplies rows.

**Include financial reports on listings** — flip `include_financial_reports=True` in the route and
add `selectinload(ListingDB.listing_financial_reports)` inside `_build_select_clause`. Without it
a 50-listing market issues 51 queries. See Problem 7 for the `location` side effect.

**`GET /api/exchange-rate`** — new `api/routes/exchange_rate.py`,
`APIRouter(prefix="/api")`, registered in `api/app/main.py`. Body is
`services.exchange_rate.resolve_cop_per_usd(db_session)`, which already handles the cold-start
fetch-and-store. Response carries `cop_per_usd` **and** `record_date`, which the UI must display.
`None` → **503, not 200-with-null**: a currency toggle with no rate is a broken feature, not an
empty result.

---

## Chunk 3 — Property reads and the analysis envelope (backend)

**Sensitivity: computed, not persisted.** Every input the sweep needs is already on the row —
`purchase_price_cop`, `annual_revenue_cop` and all seven percentage knobs — so the cells are a
pure function of it. A column would mean a migration, an entity field, a factory field and model
tests for no read-path saving, and would freeze `DEFAULT_SENSITIVITY_FACTORS = (0.9, 1.0, 1.1)` —
a presentation choice — into the schema.

The honest cost: the deep-dive page reloads via `GET`, not `POST /analyze`, so that route must
rebuild a scenario from the stored report. That is a new
`services/property_analysis.scenario_from_report(report) -> PropertyScenario` — about fifteen
lines, independently testable, and worth having regardless: it is the guarantee that a stored
report can always be re-explained. **Its round-trip test —
`analyze(scenario_from_report(r))` reproduces `r`'s CoC return within float tolerance — is the
single most valuable test in this chunk.**

The same argument covers `MonthlyExpenseBreakdown` (finding 9), so both ride one envelope:

```python
class PropertyAnalysisData(BaseResponseModel):
    report: PropertyFinancialReportEntity
    expenses: MonthlyExpenseBreakdown
    sensitivity: list[SensitivityCell]

class PropertyAnalysisResponse(BaseResponseModel):
    data: PropertyAnalysisData
```

This **changes the shape of `POST /api/properties/{id}/analyze`** — `data` is currently the report
itself. Nothing consumes it yet (no frontend; backend tests only), so now is the moment. Call it
out in the PR description.

**Three new routes** in `api/routes/properties.py`:

| Route | Why |
| :--- | :--- |
| `GET /api/properties` | Decision 7's persistent list. Needs `PropertyFacade.get_all()` ordered `created_at DESC`. |
| `GET /api/properties/{id}` | Deep-dive header. |
| `GET /api/properties/{id}/report` | **Load-bearing.** Latest persisted `PropertyAnalysisData` with **no AirROI call**, via `PropertyFinancialReportFacade.get_latest_by_property_id` + `scenario_from_report`. Without it every deep-dive page load costs $0.01 and rewrites the comp set, and a react-query refetch-on-focus or a StrictMode double-mount doubles it. Returns `{"data": null}` with 200 for a never-analysed property, matching the `/comps/cached` precedent. |

**Comps with the listing joined (decision 5).** Add `listing: Mapped["ListingDB"] = relationship()`
to `PropertyCompDB` (FK exists; no migration) and `selectinload(PropertyCompDB.listing)` in
`PropertyCompFacade.get_all_by_property_id`.

Type the nested object as a **narrow** `CompListingEntity` — `airroi_id`, `baths`, `bedrooms`,
`cover_photo_url`, `latitude`, `longitude`, `name`, `property_type`, `source_url` — **not**
`ListingEntity`. The comp table's ADR / occupancy / revenue come from the frozen snapshot on the
comp row, which is the entire point of that snapshot per `PropertyCompDB`'s docstring; the listing
supplies only name, type, bedrooms, baths and the Airbnb link. A full `ListingEntity` would ship a
400-character description, thirteen amenities and twenty photo URLs per comp × 25 comps for a
table that renders none of it, *and* drag `listing_financial_reports` into a second N+1.

**`extra="forbid"` on `ScenarioOverridesRequest`.** One line in `api/models/property_analysis.py`.
See Problem 4 — this is the cheapest defence against every future naming drift, and it turns a
silent wrong-number into a 422.

---

## Chunk 4 — Frontend foundation

No new dependencies. Everything here is a seam chunks 5 and 6 both need.

### Types

Five files in `frontend/src/types/`, re-exported from `main.d.ts`. Every field mirrors the Pydantic
entity name-for-name: snake_case, and `Optional[X]` → **`X | null`, not `X?`**, because the API
sends explicit `null`. (`MarketEntity.district?: string` is already wrong for this reason and
breaks under strict — fix it here.)

- **`markets.d.ts`** (amend) — `MarketFinancialReportEntity`, `MarketWithFinancialReportEntity`.
- **`properties.d.ts`** (new) — `PropertyEntity` (23 fields, exact), `PropertyCreateRequest`, and
  `MANUAL_FIELDS` mirroring `api/models/property.py`.
- **`propertyAnalysis.d.ts`** (new) — `PropertyFinancialReportEntity` (all 40 fields),
  `MonthlyExpenseBreakdown`, `SensitivityCell`, `PropertyAnalysisData`, `PropertyAnalyzeRequest`,
  and `AnnualRevenueSource = 'airroi_p25' | 'airroi_avg' | 'comp_derived' |
  'airroi_p25_thin_comps' | 'airroi_avg_thin_comps'`.
- **`comps.d.ts`** (new) — `CompListingEntity`, `PropertyCompEntity` with
  `listing: CompListingEntity | null`.
- **`exchangeRate.d.ts`** (new) — `cop_per_usd`, `record_date`.

### Utilities — where decision 12's unit tests live

| Module | Purpose |
| :--- | :--- |
| `src/utils/unwrapEnvelope.ts` | `unwrapEnvelope<T>(res): Promise<T>`, throwing on `!res.ok` using `detail`. **Today `fetchy.get(...).then(r => r.json())` treats a 500 as a react-query success with `data === undefined`** — which is why `MarketsList` renders an empty grid and no toast on a backend error. Retrofit the two existing queries. |
| `src/common/utils/currency.ts` | `convertCopToUsd` returning `null` when either input is unusable (mirrors the backend); `formatCop` / `formatUsd` via `Intl.NumberFormat`. |
| `src/common/utils/investmentFit.ts` | The fit score and `medianPurchasePriceCop`. |
| `src/common/utils/metricThresholds.ts` | `cocReturnTone(pct, confidence)` → `'good' \| 'fair' \| 'poor' \| 'unrated'`. |
| `src/common/utils/dataConfidence.ts` | `dataConfidence(source, compCount)` → `{ level, message }`. |
| `src/common/utils/charts.ts` | `barGeometry(values, {width, height})` → pure `{x, y, w, h}` tuples. |
| `src/common/utils/propertyAnalysis.ts` | `reportToScenarioOverrides(report)` — the one place `interest_rate` → `interest_rate_percentage` happens, with a test asserting it. |

### Currency context

`src/providers/CurrencyProvider.tsx` + `useCurrency()`, state in `localStorage`. The hook
**refuses to convert without an explicit `{rate, rateAsOf, rateSource}`**. Making the rate a
required argument is what makes silent mixing of a live rate with a report's frozen rate
impossible. Toggle goes in `TopNavBar` beside the light/dark button.

### Mock-server plumbing

Real work the decisions imply but do not name:

- `buildPathToGzippedData` takes only `<entityType>/<prefix>__data.json.gz` — `properties/{id}/comps`
  has no representation. Extend `EndpointConfig` with `subPath?` and join extra segments.
- `buildRoutePath` knows only `list` and `overview`, and hardcodes `:entityId` where
  `buildMirageStorybookRoutePath` uses `config.entityIdPathParam`. Unify them, add the
  sub-resource case.
- **`mirageTestServer.ts` registers `this.get` only.** Add `this.post`. `safeGetBodyJson` already
  exists in `mock-data-server/utils/requests.ts`, unused — it was written for exactly this.
- New `endpointConfigs` entries for exchange-rate, properties list/overview/report/comps, and the
  two POSTs.

### Fixtures

Regenerate `markets/list__data.json.gz` and the three `markets/<uuid>__data.json.gz`; add
exchange-rate, properties list/overview/report/comps. **There is no tooling for this** — they are
hand-captured `curl | gzip`. Write `scripts/capture-fixtures.sh` in this chunk; six by hand now
and six more every time a shape changes is not sustainable.

Include **one Calima property fixture with `comp_count: 1` and
`annual_revenue_source: "airroi_p25_thin_comps"`**. That is the case the confidence UI exists for
and the one most likely to be "fixed" into a false positive.

### TS strict for new code, and a CI that enforces it

`frontend/tsconfig.strict.json` extending `tsconfig.common.json` with `"strict": true` and an
`include` naming only the Phase-4 directories; add to `tsconfig.json` references and
`pnpm build:types`.

**This is decorative unless CI runs it** (finding 8). Add to `.github/workflows/frontend-test.yml`
before the test step:

```yaml
      - name: "🔎 Typecheck"
        working-directory: ./frontend
        run: pnpm build:types
      - name: "🧹 Lint"
        working-directory: ./frontend
        run: pnpm lint
```

Expect a first-run blast radius into shared files: `Toast`'s
`alertSeverity?: 'error' | 'success'` receives react-query's `status`, which can be `'pending'` —
a type error that compiles today only because strict is off, and `MarketsList` does exactly this
at line 44. Fix `Toast`'s props (and its hardcoded "while fetching market overview data" fallback)
here, since every new page reuses it.

---

## Chunk 5 — Step 11, market overview screen

Route `/markets` stays; the page is rewritten. Follow the **`MarketOverview` pattern, not
`MarketsList`'s**: `marketsListQuery` as `queryOptions`, a `marketsListLoader(queryClient)`
calling `ensureQueryData`, `useSuspenseQuery` in the component. This also fixes `MarketsList`
gating on `isFetching`, which blinks the whole grid to a spinner on every background refetch —
use `isPending`. `staleTime: 1000 * 60 * 60` per Step 10.

New components under `src/pages/markets/MarketsList/components/`:

| Component | Notes |
| :--- | :--- |
| `MarketCard` | Presentational; props `market`, `rate`, `budgetCop`. MUI `Card`, `FlexRow`/`FlexColumn`. Metrics: ADR, occupancy, annual revenue, `Math.round(listing_count)` labelled **"avg. active listings (12 mo)"** — the value is a float (6375.8), and rendering it raw reads as a bug. Peak months as MUI `Chip` pills; null → "Peak months not yet available" (a new market has none until two cron runs pass). |
| `MarketCard/BudgetIndicator` | `Math.floor(BUDGET_COP / medianPriceCop)`, or `Not enough price data (N)` below n=3. |
| `FitScoreBadge` | Score 0–100 plus the thin-market flag. |
| `MarketSortControls` | MUI `ToggleButtonGroup`: fit (default) · ADR · occupancy · revenue. |
| `ColombiaMap` | `MapContainer` copied from `ListingMapCard`; one `Marker` per market with a non-null centroid; click sets `selectedMarketId`, scrolling the card into view. Drop `useMap` — `ListingMapCard` imports it and never uses it. |

`BUDGET_COP = 1_766_000_000` in `src/constants/index.ts` with the doc reference.

Stories go on the presentational components (props only, no Mirage) so `storybook:build` stays
green. Page test is Mirage-backed: 8 cards, default order fit-descending, resort by ADR reorders,
a report-less market renders the empty state, currency toggle flips the money.

### Investment fit score

`src/common/utils/investmentFit.ts`. **Anchors are absolute and in COP, deliberately.** COP
because `adr_usd` and `annual_revenue_usd` are always NULL (finding 5) and because a
rate-dependent score would silently reorder the list between renders. Absolute rather than
min-max because a min-max score always pins one market at 100, tells you only which served row is
least bad, reorders every other market when one is added, and makes every unit test depend on the
whole fixture set.

```
norm(x, lo, hi) = clamp((x - lo) / (hi - lo), 0, 1)

R = norm(annual_revenue_cop, 12_000_000, 60_000_000)   // ≈ $3,000 – $15,000
O = norm(occupancy_rate,     0.15,       0.55)
A = norm(adr_cop,            120_000,    880_000)      // ≈ $30 – $220
D = clamp(1 - (log10(max(listing_count,1)) - log10(50)) / (log10(10_000) - log10(50)), 0, 1)

fit  = round(100 * (0.40*R + 0.30*O + 0.15*A + 0.15*D))
thin = listing_count < 30
```

**Justification.** Revenue carries the most weight because it is the outcome variable and —
verified above — it is *not* `ADR × occupancy × 365` in AirROI's data, so it is an independent
measurement rather than a restatement of the other two. Occupancy is second: it is the reliability
axis the doc itself names and the one that most separates the markets (0.18 → 0.40). ADR gets half
that weight because it is partly inside revenue already; its marginal information is
operating intensity — at equal revenue, a higher-ADR market earns it over fewer nights, meaning
fewer turnovers and cleans. Depth is inverse-log because saturation is a real cost (Bogota's 6,376
listings) but the relationship is plainly logarithmic; it carries the smallest weight because it
has the weakest evidence behind it.

`thin` is a flag, **not an adjustment**. Pance's 27.8 listings score 1.0 on depth, which reads as
"no competition" when the truth is "no market". Render "Thin market (28 listings)" beside the
badge rather than fudging `D`. Same discipline as the comp-count warning: state the number, state
how much to trust it, never silently move it.

Sanity check against the real seeded data:

| Market | R | O | A | D | **Fit** |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Pance | 0.33 | 0.45 | 0.37 | 1.00 | **47** (thin) |
| Calima | 0.41 | 0.08 | 0.97 | 0.76 | **45** |
| Salento | 0.29 | 0.48 | 0.29 | 0.56 | **38** |
| Bogota | 0.10 | 0.63 | 0.09 | 0.09 | **25** |

That reproduces the doc's own Part 1 ranking (Calima/Pance top, Salento third, Bogota last) from
real API data rather than the doc's fictional numbers. Every score lands under 50, which is
honest — no market clears half the anchor band. Document that the anchors are a calibration
constant to revisit once the four new markets land in chunk 1; that is the moment the real range
is known. The UI must label the score a derived heuristic, not a datum.

---

## Chunk 6 — Steps 12–13, property section

Three routes in `browserRouter.tsx`. Add `PROPERTIES: '🏠 Properties'` to `navItemsLabels` —
`NavDrawer` filters on membership there, so `/properties/new` and `/properties/:id` are correctly
hidden by having no label.

| Route | Screen |
| :--- | :--- |
| `/properties` | List of saved candidates; `propertiesListLoader`. |
| `/properties/new` | Create form. |
| `/properties/:propertyId` | Deep-dive; `propertyOverviewLoader`. |

### `/properties/new` — URL-first, with a map picker

The all-or-nothing manual validator is worse than it first appears: `MANUAL_FIELDS` includes
**`latitude` and `longitude`**, and there is no geocoder in this codebase. Nobody types
`4.5709, -74.2973` into a form. And `source_url` is required even for manual entry (`NOT NULL`,
uniquely constrained), so a private off-market sale needs a fabricated URL.

Ship it as one prominent **Finca Raiz URL** field with a primary submit; below it a disclosure
("This isn't a Finca Raiz listing") expanding the full nine-field manual panel as a single unit,
with the server's own error mirrored inline. **Lat/lng are set by clicking a react-leaflet map** —
`ListingMapCard` is the template, the dependency is installed, and it turns the worst field on the
form into the easiest. Label `source_url` on the manual path as "Listing or reference URL (any
unique URL; used to prevent duplicates)" and say plainly that re-submitting a URL updates the
existing property rather than creating a second.

React state, no form library, per the doc. Defaults pre-loaded from Part 6 constants. **This is
the first `useMutation` in the repo** — it needs `retry: false` and a submit disabled while
pending, because `POST /analyze` inserts a **new row every call** (`create_or_update` with no `id`
inserts), so a double-click writes two reports and spends two AirROI calls.

Sequence: `POST /properties` → `navigate('/properties/{id}')` → deep-dive loader
`GET /properties/{id}/report` → null → render an "Analyse" panel with the assumption sliders →
`POST /analyze` → invalidate. **Do not chain both POSTs behind one button.** Splitting them makes
a scrape failure recoverable without re-entering the form, and puts the analysis inputs on the
page that displays their results.

### `/properties/:propertyId` — deep-dive

The loader `ensureQueryData`s three queries in parallel: property, report (`staleTime` 1h), cached
comps (`staleTime` 30 min per Step 10). All three are `GET`. **`POST /analyze` is never in a
loader** — react-router data mode would re-run it on every navigation.

| Component | Notes |
| :--- | :--- |
| `DataConfidenceBanner` | **Above** the metric grid, not a footnote. `comp_derived` & ≥10 → Good; `comp_derived` & 5–9 → Fair; any `_thin_comps` → **"Low confidence — AirROI's model only, N comparable listing(s)."** For Calima N is 1, and that comp was a 5br/5.5ba/16-guest property returned for a 2br query. |
| `MetricGrid` | 3×3 per the doc. CoC and payback via `cocReturnTone` — and **`'unrated'` (neutral grey, number still shown) whenever confidence is Low.** Colour is a recommendation; you do not recommend off n=1. |
| `RevenueComparisonRow` | AirROI direct vs comp-derived, winner labelled from `annual_revenue_source`. Add the **p25/p50/p75/p90 spread** as a horizontal range bar with the chosen figure marked — Step 6 measured p90 at +94% over the mean, far more informative than a ±10% sweep, and it is already on the row. |
| `ExpenseBreakdownCard` | The five lines off `data.expenses`. |
| `SensitivityTable` | Three columns off `data.sensitivity`, headed −10% / base / +10% **revenue**. Carry `calculations.sensitivity`'s own reasoning as help text. Do not build the doc's grid; it is arithmetic theatre. |
| `SeasonalityChart` | Plain SVG — see below. |
| `AssumptionsPanel` | Sliders seeded via `reportToScenarioOverrides(report)`; re-analyse via `useMutation`. |
| `PropertyCompsTable` | `@tanstack/react-table` **with `getSortedRowModel`**, default revenue desc. Columns: name (linking `listing.source_url`, new tab), property type, bedrooms, ADR, occupancy, est. annual revenue, `distance_km`. "Refresh comps" → `GET /comps` + invalidate, with the AirROI cost in the tooltip. |

`ListingFinancialReportsTable` derives columns from `Object.keys(rows[0])` and has no sorting.
**Do not copy it** — take its `flexRender`/`useReactTable` skeleton and declare columns explicitly.

### The 12-month seasonality chart — plain SVG

The data is twelve floats summing to 1.0. The entire charting requirement is
`y = value / max * height`.

- **d3 (installed, never imported).** You would use `scaleLinear` and `scaleBand` — four lines of
  arithmetic. Against that: `vite.config.ts` groups all of `node_modules` into one `vendor` chunk
  with no per-module tree-shaking guarantee, so importing the `d3` meta-package adds roughly 90 kB
  gzipped for a division. d3's imperative DOM ownership also fights React 19 — you end up with a
  `ref` + `useEffect`, producing no queryable roles for RTL and nothing for
  `@storybook/addon-a11y` to check. **Reject.** (Separately: `d3` is a zero-import dependency
  today. Either this chunk uses it or it should be removed — flag the one-line diff.)
- **MUI.** `@mui/x-charts` is not installed; `@mui/material` and `@mui/lab` have no chart
  primitives. A new dependency for one bar chart. **Reject.**
- **Plain SVG in JSX.** Twelve `<rect>`s and twelve `<text>`s over a `viewBox`, geometry from the
  pure `barGeometry()` helper — unit-testable in isolation, exactly the seam decision 12 wants.
  Each bar carries a `<title>` so `getByTitle('July — 12.4% of annual revenue')` works in RTL and
  the a11y addon sees real accessible names. **Recommended.**

Draw two reference lines the other options make awkward: solid at the annual mean (1/12 = 8.33%)
and dashed at the doc's +15% threshold (9.58%). That turns twelve bars into an argument, and shows
visually why `peak_months` uses top-3 rather than the doc's +15% rule — Step 6 measured the Bogota
2br capture clearing that threshold in *zero* months.

Market cards get pills, not this chart, until chunk 1's `monthly_revenue_distribution` column lands.

### Currency: the rate that produced a number is the rate that converts it

Three cases, one rule:

- **Property report** — `report.exchange_rate` wins absolutely. Every `_usd` column was computed
  with it; re-deriving from today's rate would show a USD net income that does not equal
  `annual_revenue_usd − 12 × monthly_expenses_usd` from the same row. The toggle picks a stored
  column and does **no arithmetic at all**.
- **Market cards** — `adr_usd` / `annual_revenue_usd` are NULL in every row (finding 5), so the
  live rate is the only option. It is also the right one: market figures are a rolling 12-month
  average with no single moment of calculation, so there is no rate they were "computed at".
  Leave those columns NULL and mark for a later drop rather than backfill them, precisely to
  avoid creating the ambiguity.
- **Comps** — COP only, no USD sibling. Convert with `report.exchange_rate` when a report exists
  so comps sit on the same footing as the analysis they produced; live rate otherwise.

They *will* disagree. Make that visible rather than reconcilable: "converted at COP 4,013 / USD ·
12 Aug 2026 (as analysed)" on the property page, "COP 4,087 / USD · today" on markets.
`useCurrency()` requiring `{rate, rateAsOf, rateSource}` makes silent mixing impossible. The fit
score is COP-anchored on purpose, so no sort order depends on any of this.

---

## Chunk 7 — Step 14, deploy gaps

1. **CORS.** `origins` in `api/app/main.py` holds only the Railway frontend. Production is
   correct; local is broken in one specific way: `docker-compose.yml` publishes vite on
   `localhost:5173` with **no vite proxy**, so `API_SERVER_DOMAIN` resolves to
   `http://localhost:5173`, `/api/*` hits the dev server and 404s — and setting
   `VITE_API_SERVER_DOMAIN=http://localhost` (nginx) then trips CORS. Add `http://localhost:5173`,
   `http://localhost:3003`, `http://localhost:6006`, `https://aoam.dev` and `http://aoam.dev`,
   gating the localhost entries on `not is_prod()`. `TrustedHostMiddleware` already allows
   `localhost` and `aoam.dev`. The `:6006` entry matters because Storybook talks to the express
   mock server on `:3030`, whose `cors()` list already names `:6006` and `:3003` — mirror it.
2. **`VITE_API_SERVER_DOMAIN`.** Absent from `.env.example`, absent from `frontend/README.md`, no
   `frontend/.env*` exists, and `src/constants/index.ts` carries a hardcoded prod fallback keyed
   on a hostname substring plus two unconditional `console.log`s that ship to production. Document
   it in both files with the three resolution cases; move the logs behind `import.meta.env.DEV`;
   keep the Railway fallback but give the TODO an expiry condition.

---

## Problems worth knowing before you start

1. **`properties` has no `market_id`** (finding 3) — the budget indicator has no join key.
   Scoped into chunk 1 as a migration plus nearest-centroid resolution.
2. **The budget indicator is invisible on day one, in production, indefinitely.** It needs n≥3
   properties per market and `properties` rows are only ever created by a user POST. Every card
   ships "Not enough price data (0)" until someone hand-enters 24 Finca Raiz URLs. Hence
   `seed_properties.py` in chunk 1 — it is also the only way to get a meaningful test fixture.
3. **Fixtures need regenerating and there is no tool.** Adding `financial_report` does not break
   `MarketsListData` (extra key) or Mirage (it serves whatever the `.gz` holds), but the new
   `MarketCard` reads `market.financial_report`, which will be `undefined` in the old fixture — so
   every new page test renders the empty state and **passes vacuously**. Write the capture script.
4. **`interest_rate_percentage` vs `interest_rate` is a silent wrong-number bug.** The obvious
   implementation of "re-analyse with different assumptions" seeds the form from the stored report,
   whose column is `interest_rate`. Submitted back as `interest_rate`, `PropertyAnalyzeRequest` —
   a plain pydantic `BaseModel` — **ignores the extra key**, `overrides()` omits it, and
   `PropertyScenario` silently applies its 10% default. The user sets 14%, the page reruns, and the
   number returned was computed at 10%. Do both defences: `extra="forbid"` (chunk 3) and the
   explicit TS mapper with a test (chunk 4).
5. **`annual_revenue_source` and `comp_count` must disable the colour coding, not just add a
   note.** A CoC return rendered green off Calima's single 5br/16-guest comp is the most dangerous
   pixel in this app. Hence `'unrated'`.
6. **`include_financial_reports=True` changes the `location` string.** `_build_select_clause`
   returns `select(ListingDB)` in that mode, so `location` is no longer `ST_AsText(...)` — the
   entity rebuilds WKT from `latitude`/`longitude`, which are `REAL` (float4) while the geography
   renders float8. The same listing will report a different `location` from `/api/listings/{id}`
   than from `/api/markets/{id}`. Any fixture or test comparing across the two will break.
7. **`queryClient` is a module-level singleton** exported from `browserRouter.tsx`.
   `WithMemoryRouter` re-imports `routerConfig` from the same module, so loaders in tests close
   over the *app's* client while the test wraps a fresh one. `MarketsList` gets away with it today
   because it uses `useQuery` directly; loader-based pages will populate one cache and read
   another. Inject the client, or have the test pass the same one.
8. **Storybook stories that fetch need the express mock server on :3030.** Keep every story on a
   presentational component taking props — already the repo's container/presenter split — or
   `storybook:build` and Chromatic produce broken frames.
9. **`PropertyCreateRequest.notes` is free text and `services/finca_raiz.py` writes JSON into it.**
   A `notes` textarea on the new form will overwrite scraped JSON that `_notes_number()` still
   reads as a fallback in `_resolve_baths`. Either disable `notes` on the scrape path, or stop
   `_resolve_baths` falling back to it.

---

## Verification

**Backend**
- `docker compose run --rm backend-test` — existing suite green, new route tests pass.
- The `scenario_from_report` round-trip test is the acceptance gate for chunk 3.
- Audit query output pasted into this document for chunk 1.
- `curl` every new endpoint through `https://aoam.dev/api/...` and via `/docs`.

**Frontend**
- `pnpm test` (vitest). Note `fetchy.test.ts:163` is `it.skip`, **not** a live failure — the suite
  is not red today and should stay that way.
- `pnpm build:types` and `pnpm lint` — newly enforced in CI by chunk 4.
- Unit tests: fit score (against the four-market table above), budget median + n≥3 threshold,
  currency conversion, CoC tone incl. `'unrated'`, comp sorting, `barGeometry`,
  `reportToScenarioOverrides`.
- Mirage-backed page tests for `/markets`, `/properties`, `/properties/new`, `/properties/:id`.
- `pnpm storybook:start` — stories for the presentational components.

**End-to-end, `docker compose up all -d` at `https://aoam.dev`**
1. `/markets` — cards show ADR, occupancy, revenue, peak-month pills, rounded listing count; map
   places a marker per market; sort controls reorder; budget indicator shows a figure or the
   "not enough price data" message.
2. `/properties/new` — paste a live Finca Raiz Salento or Calima URL; property created with COP
   price and USD conversion. Then exercise the manual path and confirm the map picker sets lat/lng.
3. `/properties/:id` — analyse with Colombian defaults; all 9 metrics render, revenue comparison
   labels the conservative figure and shows the percentile spread, sensitivity shows 3 cells,
   the 12-bar chart renders with both reference lines.
4. **Analyse a Calima property specifically** — confirm the low-confidence banner appears *and*
   that CoC/payback render grey rather than green. This is the case the whole thing exists for.
5. Comps table loads from cache, sorts, links out to Airbnb; "Refresh comps" re-fetches.
6. Toggle currency; confirm a report's USD values reconcile against its own stored
   `exchange_rate`, and that the rate and its date are displayed.

---

## Out of scope

- Flipping global TypeScript `strict` and `@typescript-eslint/no-explicit-any` (follow-up).
- Removing the dead `frontend/src/store/` scaffolding and the unmodified `frontend/src/stories/`.
- Vercel deployment.
- Any change to the AirROI ingestion cadence or the Finca Raiz scraper.
- Renaming the `interest_rate` column (see Problem 4 — `extra="forbid"` buys more for less).
