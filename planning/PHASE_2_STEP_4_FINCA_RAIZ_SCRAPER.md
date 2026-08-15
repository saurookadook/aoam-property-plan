# Phase 2 / Step 4 — Finca Raiz Price Scraper

Implementation plan for `docs/COLOMBIA_STR_EXECUTION_PLAN_v3.md` → Part 3 → Phase 2 → Step 4.

---

## Context

Phase 2 / Step 4 calls for a scraper that turns a Finca Raiz listing URL into a persisted
`properties` row with an asking price in COP and USD. It is the last missing input to the
Step 5 calculation engine — without a purchase price there is no cash-on-cash return, no
payback period, and no way to test a real candidate property against the AirROI market data
already flowing into the database.

The codebase has moved well past the doc. Markets, listings, exchange rates, and both
financial-report tables are live; `properties` exists with a full column set and a factory,
but nothing writes to it. Two things in the doc are wrong on contact with reality and this
plan corrects them:

1. **The site is not scraped with BeautifulSoup.** `fincaraiz.com.co` is a Next.js app that
   embeds the entire listing record as JSON in `__NEXT_DATA__`.
2. **The `properties` schema cannot hold what the site returns.** `postal_code` is
   `NOT NULL` and Finca Raiz never provides it; `purchase_price_cop` is `NOT NULL` but
   listings can set `hidePrice`.

**Outcome:** `POST /api/properties` accepts either a Finca Raiz URL or a manual body and
returns a persisted property with price in COP and USD. This is also the first `POST` route
in the codebase and the first `services/` module — it sets the pattern for Step 5
(`calculations.py`) and Step 6 (`airroi.py`).

---

## Verified against the live site

Probed `https://www.fincaraiz.com.co/casa-en-venta-en-ahitamara-salento/193301244` (a real
Salento listing) — HTTP 200 to a plain browser UA, no Cloudflare challenge, and
`robots.txt` `User-agent: *` does not disallow listing detail paths.

| `properties` column | `__NEXT_DATA__` path (`props.pageProps.data`) | Live value |
| :--- | :--- | :--- |
| `purchase_price_cop` | `price.amount` | `700000000` |
| `latitude` / `longitude` | `latitude` / `longitude` | `4.57076` / `-75.640629` |
| `bedrooms` | `bedrooms` | `5` |
| `property_type` | `property_type.name` | `"Casa"` |
| `city` | `locations.city[0].name` | `"Salento"` |
| `state` | `locations.state[0].name` | `"Quindio"` |
| `country` | `locations.country[0].name` | `"Colombia"` |
| `neighborhood` | `locations.neighbourhood[0].name` | `"Ahitamara"` |
| `address` | `address` | `"CASA 1 MZ B/AHITAMARA/EL LIMONAR"` |
| `source_created_at` | `created_at` | `"2026-01-21"` |
| `postal_code` | — | **absent** |

Also present and worth capturing in `notes`: `commonExpenses.amount` (HOA / administración
in COP — a direct Step 5 input), `m2`, `stratum`, `bathrooms`.

**Do not use `data.price_amount_usd`.** It is `217599`, implying a rate of 3216.92 COP/USD.
Frankfurter is ~4150. Mixing that into a financial report alongside AirROI revenue converted
at our own rate would silently corrupt the CoC and payback math.

---

## Decisions

| Decision | Choice |
| :--- | :--- |
| Extraction | Three tiers: `__NEXT_DATA__` → JSON-LD → BeautifulSoup |
| `postal_code` | Migration to nullable |
| Scope | Service + `POST /api/properties` (pulls Step 8's route forward) |
| USD source | Our `exchange_rates` table; live frankfurter fetch on cold start |
| Duplicates | Upsert on `source_url` (unique index) |
| Sold / hidden-price listings | Persist, flagged via a `status` column |
| Manual entry | One endpoint, `source_url` XOR manual body |
| Module home | Top-level `backend/services/` |
| Alt sources (metrocuadrado, fincainca) | Out of scope; host-keyed resolver leaves the seam |

---

## Implementation

### 1. Migration — `backend/db/migrations/versions/`

New revision, `down_revision = "7abfe7783ffd"` (current head, from
`2026_07_15_0020-..._add_fields_to_listings.py`). Follow the style of
`2026_06_07_1427-f168cdcd9455_alter_columns_on_properties.py` — explicit `op.alter_column`
with `existing_type`, and a real `downgrade()`.

- `properties.postal_code` → `nullable=True`
- `properties.purchase_price_cop` → `nullable=True` (needed for `hidePrice` listings)
- Add `properties.status` — `TEXT`, `nullable=False`, `server_default="active"`
- Unique index on `properties.source_url`

The naming convention in `db/base_db.py` yields `properties_source_url_key` for the unique
constraint — name it explicitly so `downgrade()` can drop it.

### 2. Model layer

- **`backend/models/property/db.py`** — mirror the migration: relax `postal_code` and
  `purchase_price_cop`, add `status: Mapped[str]`.
- **`backend/models/property/entity.py`** — `postal_code: Optional[str] = None`,
  `purchase_price_cop: Optional[float] = None`, `status: str`.
- **`backend/models/property/facade.py`** — add `get_one_by_source_url()` raising
  `PropertyFacade.NoResultFound`, and extend `_find_one_if_exists()` to try `id` then
  `source_url`. This is the exact shape `ExchangeRateFacade._find_one_if_exists()` already
  uses for `record_date` — copy it rather than inventing a variant. `create_or_update()`
  needs no change once `_find_one_if_exists` knows about `source_url`.
- **`backend/models/exchange_rate/facade.py`** — add
  `get_latest_on_or_before(record_date)` → `Optional[ExchangeRateEntity]`, ordering
  `record_date` descending with `LIMIT 1`. Returns `None` rather than raising; the caller
  branches on it.
- **`backend/_factories/property/db.py`** — add `status = "active"` so existing factory
  callers keep working.

### 3. `backend/services/` (new top-level package)

Add `"services"` to `[tool.hatch.build.targets.wheel] packages` in `backend/pyproject.toml`,
alongside `beautifulsoup4` in `[project] dependencies`. `requests` is already a prod
dependency — do not add `httpx` (it is dev-only, used by `TestClient`).

**`services/property_source.py`** — host-keyed resolver. `_PARSERS = {"fincaraiz.com.co":
...}`; `parse(url, html)` normalises the host (strip `www.`) and raises `UnsupportedSource`
for anything unregistered. Adding metrocuadrado later is a new module plus one registry
entry.

**`services/finca_raiz.py`** — fetch and parse. No database access; returns a plain dict for
`PropertyFacade.create_or_update()`.

- `fetch(url)` — `requests.get` with a browser UA and `timeout=30`, matching the timeout
  already used throughout `api/crons/handlers.py`. On-demand only, no scheduling.
- Tier 1 `_parse_next_data(html)` — regex out `<script id="__NEXT_DATA__" ...>(.*?)</script>`,
  `json.loads`, map `props.pageProps.data` per the table above. **Note:** the tag carries a
  `crossorigin` attribute, so a naive `id="__NEXT_DATA__">` match fails — the regex must
  allow attributes between the id and `>`.
- Tier 2 `_parse_json_ld(html)` — `<script type="application/ld+json">`. Yields
  `priceSpecification.price` (labelled `COP`), `object.address`, `object.geo.latitude` /
  `.longitude`. It is `@type: "RentAction"` even on a sale listing — ignore `@type` entirely,
  it is unreliable.
- Tier 3 `_parse_dom(html)` — BeautifulSoup, only for what tiers 1–2 cannot supply:
  `city` / `state` / `neighborhood` from the breadcrumb, `bedrooms` and `property_type` from
  the feature list. Keep the selectors in one module-level dict so a redesign is a
  single-place fix.
- Merge tiers in order, first non-`None` wins. Raise `ScrapeError` only if the merged result
  still leaves a required field empty.
- Status: `price_hidden` if `hidePrice`, `sold` if `sold`, `inactive` if not `active`, else
  `active`. Evaluate in that precedence order.
- Capture `commonExpenses.amount`, `m2`, `stratum`, `bathrooms` into `notes` as JSON — no
  schema churn now, and Step 5 gets a real HOA figure instead of the doc's default.
- Exceptions: `ScrapeError` (base), `UnsupportedSource`, `FetchError`.

**`services/exchange_rate.py`** — `resolve_cop_per_usd(db_session, on_date)`:
`ExchangeRateFacade.get_latest_on_or_before()`, and if that is `None`, fetch live from
`https://api.frankfurter.dev/v2/rates?base=USD&quotes=COP&date=...` (same URL shape and
response list-of-`{base,quote,date,rate}` as `handle_exchange_rate`), persist via
`create_or_update`, and return it. This closes the cold-start gap left by
`handle_exchange_rate`, which only writes a rate row when a `listing_financial_report` exists
for that date.

> Deliberately **not** in scope: refactoring `handle_exchange_rate` to drop that
> `listing_financial_report` guard. Flagging it — the guard means a fresh environment can run
> the cron and still end up with an empty `exchange_rates` table.

### 4. API layer

**`backend/api/models/property.py`**

- `PropertyCreateRequest(BaseModel)` — `source_url: Optional[str]` plus every manual field
  optional, with a Pydantic v2 `@model_validator(mode="after")` enforcing *either*
  `source_url` *or* the full manual set. FastAPI surfaces a violation as a clean 422.
- `PropertyResponse(BaseResponseModel)` with `data: PropertyEntity`, matching
  `api/models/listing.py`.

**`backend/api/routes/properties.py`** — `properties_router = APIRouter(prefix="/api")`,
`logger = init_logging(__file__)`, `API_DB_SessionDependency` for the session. Follow the
try/except/`HTTPException` shape in `api/routes/listings.py`.

`POST /api/properties`:

1. If `source_url` — resolve parser, fetch, parse. `UnsupportedSource` → 400,
   `FetchError` → 502, `ScrapeError` → 422.
2. Else use the manual body directly.
3. Resolve the rate and compute `purchase_price_usd = purchase_price_cop / cop_per_usd`,
   skipping when the price is hidden.
4. `PropertyFacade.create_or_update()` → upserts on `source_url`. Commit. Return 201.

**`backend/api/app/main.py`** — import and `app.include_router(properties_router)`.
`methods` in the CORS middleware already includes `POST`.

### 5. Tests

`services/_tests/test_finca_raiz.py` (with `__init__.py`) — save the real Salento page as an
HTML fixture, then derive three variants from it to exercise each tier: full, `__NEXT_DATA__`
stripped, and both JSON blocks stripped. Assert the exact live values from the table above.
Cover `hidePrice` / `sold` / `active: false` → status, and a malformed page → `ScrapeError`.
Use the existing `http_requests_mock` fixture (`conftest.py`) — this repo mocks HTTP with
`requests-mock`, not `responses`.

`api/_tests/routes/test_routes_properties.py` — follow `test_routes_markets.py`:
`test_app_client`, `test_db_session`, `PropertyDBFactory`, and assert against
`PropertyEntity.model_validate(...).model_dump(mode="json")`. Cover the URL path, the manual
path, the XOR validator rejecting both-or-neither, re-POST of the same URL updating in place
rather than inserting, and the cold-start branch where `exchange_rates` is empty and
frankfurter is called (mock it).

`models/_tests/property/test_facade.py` and `.../exchange_rate/test_facade.py` — extend for
`get_one_by_source_url`, `_find_one_if_exists` via `source_url`, and
`get_latest_on_or_before` including the empty-table `None` case.

---

## Files

**New**

- `backend/db/migrations/versions/<new>_alter_properties_for_scraper.py`
- `backend/services/{__init__,finca_raiz,property_source,exchange_rate}.py`
- `backend/services/_tests/{__init__,test_finca_raiz}.py`
- `backend/services/_tests/fixtures/finca_raiz_salento.html`
- `backend/api/models/property.py`
- `backend/api/routes/properties.py`
- `backend/api/_tests/routes/test_routes_properties.py`

**Modified**

- `backend/models/property/{db,entity,facade}.py`
- `backend/models/exchange_rate/facade.py`
- `backend/_factories/property/db.py`
- `backend/api/app/main.py`
- `backend/pyproject.toml`
- `backend/models/_tests/property/test_facade.py`
- `backend/models/_tests/exchange_rate/test_facade.py`

---

## Verification

```sh
# 1. Migration applies and reverses cleanly
docker compose run --rm backend-migrations alembic upgrade head
docker compose run --rm backend-migrations alembic downgrade -1
docker compose run --rm backend-migrations alembic upgrade head

# 2. Test suite (backend-test sets DATABASE_NAME=test_aoam_property_plan)
docker compose run --rm backend-test pytest services/_tests api/_tests models/_tests
```

**3. End to end against the real listing** — this is the acceptance criterion, and it maps
to row 6 of the doc's "What to Do Today" table:

```sh
docker compose up all -d
curl -X POST http://localhost/api/properties \
  -H 'Content-Type: application/json' \
  -d '{"source_url":"https://www.fincaraiz.com.co/casa-en-venta-en-ahitamara-salento/193301244"}'
```

Expect `purchase_price_cop: 700000000`, `city: "Salento"`, `state: "Quindio"`,
`bedrooms: 5`, `latitude: 4.57076`, `status: "active"`, and a `purchase_price_usd` near
**168,000** (frankfurter ~4150 COP/USD) — *not* 217,599, which would mean the site's own rate
leaked through.

**4. Idempotency** — re-run the same `curl`. Same `id`, `updated_at` advanced, still one row:

```sh
docker compose exec pg_database psql -U postgres -d aoam_property_plan \
  -c "SELECT count(*), min(id::text) FROM properties WHERE source_url LIKE '%193301244';"
```

**5. Manual entry** — POST a body with no `source_url` and the full manual field set; confirm
201. Then POST with both `source_url` and manual fields, and with neither; confirm 422 both
times.

**6. Swagger** — `POST /api/properties` appears at `/docs` with the request model rendered.

---

## Notes

- `docker-compose.yml` already declares a `scraper` network and a commented-out `splash`
  volume. Neither is needed — the three-tier parse works off a single `requests.get`.
- Only listing detail pages are fetched, one request per user action, no crawling. Nothing
  here approaches the `Disallow` rules in `robots.txt`.
