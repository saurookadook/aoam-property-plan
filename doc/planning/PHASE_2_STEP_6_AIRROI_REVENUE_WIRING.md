# Phase 2 / Step 6 — Wire AirROI Revenue Data Into the Calculation Engine

Implementation plan for `docs/COLOMBIA_STR_EXECUTION_PLAN_v3.md` → Part 3 → Phase 2 → Step 6.

---

## Context

Phase 2 / Step 6 wires AirROI revenue data into the calculation engine: pull comparables for a
candidate property, derive a projected annual revenue, cross-check it against AirROI's own
estimate, and persist the result with the comp set that produced it.

**Blocked on Step 5.** `services/calculations.py` and `constants/colombia.py` do not exist —
`cae1c27` committed the Step 5 *plan* only. Step 6 consumes `PropertyScenario`, `analyze()` and
`conservative_of()` from that module, so its PR lands after Step 5's, matching the one-step-per-PR
history (`#27`, `#28`, `#29`).

**Outcome:** `POST /api/properties/{id}/analyze` turns a stored property into a persisted
financial report with a comp set, revenue percentiles, and a seasonality distribution.

---

## Verified against live AirROI captures

Six real `/calculator/estimate` responses now sit in `_research/calculator/estimate/`, plus the
existing `_research/listings/` and `_research/markets/` captures. Everything below was computed
from them.

### One endpoint supplies almost the whole step

`GET /calculator/estimate?lat&lng&bedrooms&baths&guests`, auth `x-api-key`, returns:

```
location{latitude, longitude}
revenue                          annual, COP        ← equals percentiles.revenue.avg
average_daily_rate               COP
occupancy                        0.0–1.0
percentiles{revenue, average_daily_rate, occupancy}
                                 avg / p25 / p50 / p75 / p90
monthly_revenue_distributions[12]  fractions, sum = 1.000000
currency                         "COP"
comparable_listings[]            up to 25
```

`comparable_listings[]` entries are **structurally identical** to `/listings/search/market`
results — same eight blocks (`listing_info`, `host_info`, `location_info`, `property_details`,
`booking_settings`, `pricing_info`, `ratings`, `performance_metrics`), same 24 `ttm_*`/`l90d_*`
keys. The mapping in `api/crons/handlers.py:170-238` is reusable verbatim.

### The doc's `/markets/seasonality` endpoint does not exist

Part 2 sources Peak Months from `/markets/seasonality`. AirROI publishes 22 endpoints and none is
`seasonality`. `monthly_revenue_distributions` on `/calculator/estimate` is the real source.

### Direct and comp-derived estimates diverge by market

| capture | comps | direct `revenue` | comp-derived (×365) | comp actual `ttm_revenue` |
| :--- | ---: | ---: | ---: | ---: |
| salento 3br/2ba/8g | 25 | 52,217,692 | 40,427,441 | 42,680,160 |
| salento 2br/2ba/4g | 25 | 39,980,106 | 38,158,259 | 40,274,415 |
| bogota 2br/2ba/4g | 25 | 27,426,577 | 28,789,171 | 30,472,770 |
| bogota 3br/2.5ba/8g | 25 | 36,427,240 | 71,752,112 | 72,729,120 |
| **calima 2br/2ba/4g** | **1** | 44,351,110 | 134,696,790 | 134,696,790 |
| **calima 3br/4ba/8g** | **1** | 72,469,940 | 134,696,790 | 134,696,790 |

All COP. Which figure is lower flips by market — comps run 2× the direct estimate in Bogota 3br
and 0.77× in Salento 3br — so "the lower of the two" tracks comp-set composition, not downside.

### Calima has no comp depth, and the filter silently gives up

Both Calima captures returned **the same single comp**, a 5br / 5.5ba / 16-guest property —
returned for a 2br/2ba/4g query *and* a 3br/4ba/8g query. When the local pool is thin AirROI stops
honouring bedrooms/baths/guests rather than returning an empty set. Calima is the doc's
top-ranked market. A median over that single comp is not an estimate, and nothing in the response
says so.

### `revenue` is the mean, and the distribution is right-skewed

For salento 3br/2ba/8g: `revenue` = `percentiles.revenue.avg` = 52,217,692 exactly. `p50` is
46,449,197 (−11%), `p25` is 36,074,113 (−31%), `p90` is 101,136,090 (+94%).

### Peak months: the doc's two rules disagree

Doc Part 2: *"Months where ADR or occupancy exceeds the annual average by 15%+ … Flag top 3."*
Applied to `monthly_revenue_distributions` (mean share = 1/12 = 0.0833):

| capture | >15% above mean | top 3 |
| :--- | :--- | :--- |
| salento 3br | Jul, Dec | Dec, Jul, Jan |
| salento 2br | Jan, Dec | Dec, Jan, Jul |
| calima (both) | Jan, Dec | Dec, Jan, Jul |
| bogota 3br | Jul, Dec | Dec, Jul, Aug |
| **bogota 2br** | **none** | Dec, Jul, Aug |

The +15% rule returns an empty list for Bogota 2br. Top-3 is always populated. Note also that the
distribution is *revenue* share, while the doc's rule names ADR and occupancy.

### The nightly listings ingest is under-fetching (confirmed bug)

`handle_listings_by_market` sends `{"offset": i, "page_size": 10}` for `i in range(5)`. AirROI's
`offset` is a **record** offset. The saved captures prove it: `salento…page-2` is `page-1` shifted
by exactly one listing — ADRs `1,494,491 / 579,548 / 631,685 …` become `579,548 / 631,685 /
682,832 …`, 9 of 10 rows duplicated. Each market yields ~14 distinct listings per run, not 50.

### Inputs the property table cannot supply

Both `/calculator/estimate` and `/listings/comparables` **require** `bedrooms`, `baths` and
`guests`. `properties` has only `bedrooms`. Step 4 wrote `bathrooms` into the `notes` JSON string
(`services/finca_raiz.py:204-209`); `guests` exists nowhere. Empirical guests-per-bedroom across
all 132 captured comps:

| bedrooms | n | median guests | median baths |
| ---: | ---: | ---: | ---: |
| 1 | 10 | 3 | 1.0 |
| 2 | 54 | 4 | 2.0 |
| 3 | 66 | 8 | 2.0 |
| 5 | 2 | 16 | 5.5 |

### Other confirmed facts

| Fact | Evidence |
| :--- | :--- |
| Comps carry **no distance field** | only `location_info.latitude/longitude` — distance is ours to compute |
| Everything is COP | `currency: "COP"`; both crons already send `"currency": "native"` |
| No client abstraction | two inline `requests.post` in `api/crons/handlers.py`, header dict and `timeout=30` duplicated verbatim |
| No stats helpers | zero hits for `statistics`/`median`/`numpy` in `backend/` — `statistics.median` is unused |
| No PostGIS query helper | `ix_listings_location` GiST index exists; zero `ST_DWithin`/`ST_Distance` in code |
| `markets` has no coordinates | `country/region/locality/district` only — a market centroid must come from its ingested `listings` |
| Alembic head | `ac3dd77365d3` |
| `peak_months` format | `ARRAY(TEXT)`, full month names — `["June", "July", "August"]` (`models/_tests/conftest.py:42`) |
| `_research/` is mounted into `backend-test` | captures double as test fixtures |

---

## Decisions

| Decision | Choice |
| :--- | :--- |
| Step 5 dependency | Assume it lands first; Step 6 PR is blocked on it |
| Primary endpoint | `GET /calculator/estimate` — one call for estimate + comps + seasonality |
| `/listings/comparables` | Fallback only, when the inline comp set is too thin |
| Comp revenue formula | `adr × occupancy × 365` (forward projection) |
| `ttm_total_days` | Data-quality gate, not a multiplier |
| Thin comp sets | Minimum count; below it the comp-derived estimate is unavailable, not fudged |
| Conservative figure | `percentiles.revenue.p25` |
| Persisted revenue detail | avg / p25 / p50 / p75 / p90 + the 12-month distribution |
| Comp storage | `property_comps` join table **with** a frozen metric snapshot |
| Distance | Haversine in Python at write time |
| `properties.baths` / `.guests` | New nullable columns; `baths` backfilled from `notes` |
| AirROI client | `services/airroi.py` owns all four endpoints; both crons migrate onto it |
| Pagination bug | Fixed in this step |
| Market peak months | Populated from a centroid `/calculator/estimate` call |
| Routes | Step 8's analyze + comps routes pulled forward |
| Currency | `native` (COP) everywhere; our own rate for USD, never AirROI's |

---

## Implementation

### 1. Migration — one revision, `down_revision = "ac3dd77365d3"`

Follow `2026_08_15_1807-ac3dd77365d3_…` for style: `op.f(...)` names, a real mirrored
`downgrade()`, blank line after the docstring.

**New table `property_comps`** — domain columns alphabetical, then `id`, `created_at`,
`updated_at`, then FKs, then PK, per the house `create_table` ordering:

```
adr_cop           NUMERIC   null      captured_at    TIMESTAMP(tz)  not null
distance_km       REAL      null      listing_id     FK listings.id not null
occupancy_rate    REAL      null      property_id    FK properties.id not null
ttm_revenue_cop   NUMERIC   null      ttm_total_days REAL           null
unique (property_id, listing_id)
```

**`properties`** — `baths REAL` nullable, `guests INTEGER` nullable, mirroring the columns
`listings` already has. Backfill `baths` from `notes::json->>'bathrooms'` in the same revision.

**`property_financial_reports`** — add the inputs Step 5's plan flagged as missing
(`purchase_price_cop`, `assessed_value_cop`, `hoa_monthly_cop`, `management_fee_percentage`,
`maintenance_reserve_percentage`, `closing_costs_percentage`, `predial_rate_percentage`,
`renovation_budget_cop`, `monthly_mortgage_cop`), plus revenue provenance
(`annual_revenue_source TEXT`, `airroi_revenue_cop`, `airroi_revenue_p25_cop`, `_p50_`, `_p75_`,
`_p90_`, `airroi_adr_cop`, `airroi_occupancy_rate`, `comp_derived_revenue_cop`,
`comp_count INTEGER`, `monthly_revenue_distribution ARRAY(REAL)`, `peak_months ARRAY(TEXT)`).
Alter `calculated_at` to `TIMESTAMP(timezone=True)` — it was missed by `fd50b58f027e`.

ADR and occupancy percentiles are available in the response but deliberately not stored; only
revenue percentiles drive a decision.

### 2. Models

- `models/property_comp/{db,entity,facade}.py` — copy the five-facade contract exactly (nested
  `NoResultFound`, `create_or_update` → `_find_one_if_exists` → `on_conflict_do_update` →
  `flush()` → `model_validate`). Add `get_all_by_property_id`.
- **`db/migrations/env.py` must import `PropertyCompDB`** (lines 10-16) or autogenerate emits a
  `drop_table`.
- `models/property/{db,entity}.py` — `baths`, `guests`.
- `models/property_financial_report/{db,entity}.py` — the new columns; add
  `get_latest_by_property_id` to its facade, shaped like
  `ExchangeRateFacade.get_latest_on_or_before`.
- `_factories/property_comp/db.py`, and extend `_factories/property{,_financial_report}/db.py`.

### 3. `services/airroi.py` (new)

Module constants `REQUEST_TIMEOUT = 30` and `_BASE_URL` (from `constants.AIRROI_BASE_URL`),
private `_headers()` / `_get(path, params)` / `_post(path, body)`, and `AirROIError` added to
`services/exceptions.py`. Four public functions:

| Function | Endpoint | Note |
| :--- | :--- | :--- |
| `get_revenue_estimate(*, latitude, longitude, bedrooms, baths, guests)` | `GET /calculator/estimate` | new |
| `get_comparables(*, latitude, longitude, bedrooms, baths, guests, radius=10, room_type="entire_home")` | `GET /listings/comparables` | fallback only |
| `get_market_summary(market)` | `POST /markets/summary` | moved off `handlers.py` |
| `search_listings_by_market(market, *, offset, page_size=10)` | `POST /listings/search/market` | moved; **`offset` now `i * page_size`** |

`handlers.py` keeps only DB orchestration. Its per-record `commit()` / `rollback(); commit()` /
`scoped_session.remove()` discipline stays untouched.

### 4. `services/geo.py` (new)

`haversine_km(lat_a, lng_a, lat_b, lng_b) -> float`. Python-side, because distance is computed at
write time from the API payload before any row exists. The PostGIS alternative
(`ST_Distance` over `listings.location`) is noted but not used — it would need a round-trip per
comp and the GiST index buys nothing for 25 points.

### 5. `services/property_analysis.py` (new)

`analyze_property(db_session, *, property_id, overrides) -> PropertyFinancialReportEntity`:

1. Load the property. Resolve `baths` (column → `notes` JSON → `ValueError`) and `guests`
   (column → `bedrooms × 2`, logged as an assumption). The empirical medians above show ×2
   understates 3br properties; it is deliberately the conservative direction.
2. `airroi.get_revenue_estimate(...)`.
3. Persist each `comparable_listings[]` entry through `ListingFacade.create_or_update` and
   `ListingFinancialReportFacade.create_or_update`, reusing the exact key-renaming from
   `handlers.py:218-238` (`ttm_occupancy` → `ttm_occupancy_rate`, etc.). Then write
   `property_comps` rows with `haversine_km` and the frozen metrics.
4. Comp-derived estimate: `statistics.median(adr_i × occ_i × 365)` over comps. Gate each comp on
   `|adr_i × occ_i × ttm_total_days_i − ttm_revenue_i| ≤ 10%`; log and exclude failures. Below
   `MIN_COMP_COUNT = 5` surviving comps, return `None` and set
   `annual_revenue_source = "airroi_p25_thin_comps"`.
5. Thin set → one `airroi.get_comparables(radius=10)` retry before giving up.
6. Peak months: top 3 months of `monthly_revenue_distributions` by share, as full English month
   names. **Top-3, not the +15% rule** — the latter yields an empty list for Bogota 2br.
7. Build `PropertyScenario` (Step 5) per revenue candidate, run `analyze()`, reconcile with
   `conservative_of()`. Persist with `calculated_at` stamped here, not inside `analyze()`.

Revenue arrives in COP, so no conversion is needed on the way in. USD mirrors use
`services/exchange_rate.convert_cop_to_usd` with our own rate — never AirROI's.

### 6. Cron changes — `api/crons/handlers.py`

Migrate both handlers onto `services/airroi.py`; fix `offset`. Add `handle_markets_peak_months`:
average the `location` of a market's ingested `listings` for a centroid, take median
`bedrooms`/`baths`/`guests` from the same set, call `/calculator/estimate`, write the top-3 months
to `market_financial_reports.peak_months`. This is the only route to that column —
`/markets/summary` has never returned `peak_months`, so `result.get("peak_months", None)` at
`handlers.py:80` has always been `None`. Register in `job_registry.py` and add to the
`manual_run.py` choices list and if/elif chain.

### 7. API layer

`api/models/property_analysis.py` — `PropertyAnalyzeRequest` deriving its fields from Step 5's
`PropertyScenario` rather than redeclaring them, plus `PropertyAnalysisResponse` and
`PropertyCompsResponse` on `BaseResponseModel`.

`api/routes/properties.py` — extend the existing router:

- `POST /api/properties/{id}/analyze`
- `GET /api/properties/{id}/comps` — live refresh
- `GET /api/properties/{id}/comps/cached` — from `property_comps`, no API call

`AirROIError` → 502, unknown property → 404, missing `baths` → 422, following the
`_scrape` try/except shape already in that file.

### 8. Tests

`services/_tests/test_airroi.py`, `test_geo.py`, `test_property_analysis.py`;
`api/_tests/routes/test_routes_property_analysis.py`; `models/_tests/property_comp/`.

Register every AirROI URL with the `http_requests_mock` fixture — root `conftest.py` sets
`real_http=False`, so an unregistered call fails the test. Use the six real captures as fixtures
via the `dynamic_resp_callback` pattern in `api/_tests/crons/test_handle_listings_by_market.py:38-74`.

Assertions worth naming explicitly:

- Salento 3br/2ba/8g → 25 comps persisted, comp-derived `40,427,441`, p25 `36,074,113`,
  peak months `["December", "July", "January"]`.
- **Calima → 1 comp → comp-derived is `None`**, `annual_revenue_source` records why, and the
  report still persists off p25. This is the case most likely to be "fixed" into a false positive.
- The excluded-comp gate: a comp whose `ttm_total_days` is 180 and whose formula/actual gap
  exceeds 10% is dropped and logged.
- Bogota 2br → the +15% rule finds nothing, top-3 still returns three months.
- `offset` fix: five pages request offsets `0, 10, 20, 30, 40`.

---

## Files

**New** — `db/migrations/versions/<new>_add_property_comps_and_analysis_columns.py`;
`models/property_comp/{__init__,db,entity,facade}.py`; `_factories/property_comp/{__init__,db}.py`;
`services/{airroi,geo,property_analysis}.py`; `api/models/property_analysis.py`; and the test
modules above.

**Modified** — `models/property/{db,entity}.py`; `models/property_financial_report/{db,entity,facade}.py`;
`_factories/property{,_financial_report}/db.py`; `services/finca_raiz.py` (write `baths` as a
field, not a `notes` key); `api/crons/{handlers,job_registry,manual_run}.py`;
`api/routes/properties.py`; `db/migrations/env.py`; `models/_tests/conftest.py`.

No `pyproject.toml` change — `services`, `models`, `constants` are already in
`[tool.hatch.build.targets.wheel]`, and `statistics` is stdlib.

---

## Verification

```sh
docker compose run --rm backend-migrations alembic upgrade head
docker compose run --rm backend-migrations alembic downgrade -1
docker compose run --rm backend-migrations alembic upgrade head

docker compose run --rm backend-test pytest services/_tests api/_tests models/_tests
```

End to end against the real Salento listing from Step 4:

```sh
docker compose up all -d
curl -X POST http://localhost/api/properties \
  -d '{"source_url":"https://www.fincaraiz.com.co/casa-en-venta-en-ahitamara-salento/193301244"}' \
  -H 'Content-Type: application/json'

curl -X POST http://localhost/api/properties/<id>/analyze \
  -d '{"down_payment_percentage":30,"interest_rate_percentage":10,"hoa_monthly_cop":0}' \
  -H 'Content-Type: application/json'
```

Expect `comp_count` ≥ 5, `annual_revenue_source` naming which estimate won, a `peak_months`
array of three month names, `monthly_revenue_distribution` of 12 floats summing to 1.0, and
`calculated_at` timezone-aware. Then `GET /api/properties/<id>/comps/cached` returns the same
comps with `distance_km` and makes **no** AirROI call.

Confirm the pagination fix separately — after one `manual_run listings_by_market`, a market
should hold ~50 distinct listings, not ~14:

```sh
docker compose exec pg_database psql -U postgres -d aoam_property_plan -c \
  "SELECT m.locality, count(DISTINCT l.airroi_id) FROM listings l
   JOIN markets m ON m.id = l.market_id GROUP BY 1 ORDER BY 2 DESC;"
```

---

## Notes — carried forward

- **The doc needs three corrections.** `/markets/seasonality` (Part 2) does not exist.
  `/listings/comparables` takes `room_type`, not property type, and requires `baths` and `guests`
  the doc never mentions. And Step 6's premise that comparables is a separate call is superseded —
  `/calculator/estimate` returns comps inline.
- **Calima is the doc's #1 recommended market and has one comparable listing**, which AirROI
  returns even when it matches neither the bedroom nor bath nor guest filter. Every Calima
  analysis rests on AirROI's model alone. That is an investment-thesis problem, not a code problem,
  and it deserves a decision before capital is committed.
- **The doc's market-level figures do not match AirROI.** Part 1 gives Salento 60–70% occupancy
  and $55–75 ADR; `/markets/summary` returns 34% and $85.9. Out of scope here, but Part 1's
  rankings are built on the doc's numbers.
- **`guests` is guessed.** Finca Raiz does not publish it, so `bedrooms × 2` stands in. The
  captured medians (3br → 8 guests) suggest that understates by ~25% on 3-bedroom properties,
  which biases comps toward smaller units and revenue downward.
- Step 12's sensitivity panel already needs relabelling per Step 5's plan; `percentiles` now offers
  a better spread to render than a synthetic ±10% grid.
