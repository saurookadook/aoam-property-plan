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

Beyond the doc's scope, this step also adds `name`, `description`, and `amenities` to
`properties` — the listing page carries all three, and `listings` already has the identical
columns, so capturing them now keeps the two tables symmetrical and gives the Step 12
property screen something to render besides numbers.

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
| `name` *(new)* | `title` | `"Casa en Venta en Ahitamara, Salento"` |
| `description` *(new)* | `description` | 515 chars of Spanish free text |
| `amenities` *(new)* | `facilities[].name` | `["Patio", "Servicios Públicos"]` |
| `postal_code` | — | **absent** |

Also present and worth capturing in `notes`: `commonExpenses.amount` (HOA / administración
in COP — a direct Step 5 input), `m2`, `stratum`, `bathrooms`.

### `facilities` vs `technicalSheet` — they are not the same thing

The page has two blocks that both read like "characteristics", and only one is amenities:

- **`data.facilities`** — `[{"name": "Patio", "group": "Interior"}, {"name": "Servicios
  Públicos", "group": "Interior"}]`. The real amenity list, and the semantic match for
  `listings.amenities`. **It is client-rendered — the string `Patio` appears nowhere in the
  server HTML outside `__NEXT_DATA__`.**
- **`pageProps.technicalSheet`** — server-rendered under the heading *"Detalles de la
  Propiedad"*: `Baños 4`, `Área Construida 173 m2`, `Estrato 3`, `Cantidad de pisos 1`.
  These are measurements, not amenities; they continue to go into `notes`.

Consequence for the tier design: **tier 3 (BeautifulSoup) can never recover `amenities`.** A
page that falls all the way through to the DOM parser yields `[]`. That is acceptable — the
column defaults to `{}` and is not required for a persistable row — but it must not be
treated as "this property has no amenities".

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
| `amenities` source | `data.facilities[].name` — not `technicalSheet` |
| `amenities` shape | `ARRAY(TEXT)`, identical to `listings.amenities` |
| Amenity language | Raw Spanish; ES→EN normalization deferred to Step 6 |
| `name` source | `data.title` as default, overridable via the request body |

---

## Implementation

### 1. Migration — `backend/db/migrations/versions/`

New revision, `down_revision = "7abfe7783ffd"` (current head, from
`2026_07_15_0020-..._add_fields_to_listings.py`). Follow the style of
`2026_06_07_1427-f168cdcd9455_alter_columns_on_properties.py` — explicit `op.alter_column`
with `existing_type`, and a real `downgrade()`.

Alter:

- `properties.postal_code` → `nullable=True`
- `properties.purchase_price_cop` → `nullable=True` (needed for `hidePrice` listings)

Add:

- `properties.status` — `TEXT`, `nullable=False`, `server_default="active"`
- `properties.amenities` — `ARRAY(TEXT)`, `nullable=False`,
  `server_default=sa.text("'{}'::text[]")`
- `properties.description` — `TEXT`, `nullable=True`
- `properties.name` — `TEXT`, `nullable=True`
- Unique index on `properties.source_url`

The three new content columns are a straight copy of what revision `7abfe7783ffd`
(`add_fields_to_listings`) did to `listings` — same types, same `server_default`, same
nullability. Copy that `op.add_column` block rather than re-deriving it, and mirror its
`downgrade()`, which drops in reverse order.

The naming convention in `db/base_db.py` yields `properties_source_url_key` for the unique
constraint — name it explicitly so `downgrade()` can drop it.

### 2. Model layer

- **`backend/models/property/db.py`** — mirror the migration: relax `postal_code` and
  `purchase_price_cop`; add `status: Mapped[str]`, plus `amenities`, `description`, and
  `name` copied verbatim from `models/listing/db.py` (`amenities` at line 20, `description`
  at 29, `name` at 40) so the two tables stay structurally identical.
- **`backend/models/property/entity.py`** — `postal_code: Optional[str] = None`,
  `purchase_price_cop: Optional[float] = None`, `status: str`, and — matching
  `ListingEntity` — `amenities: list[str] = Field(default_factory=list)`,
  `description: Optional[str] = None`, `name: Optional[str] = None`. Note this adds the
  first `Field` import to `property/entity.py`.
- **`backend/models/property/facade.py`** — add `get_one_by_source_url()` raising
  `PropertyFacade.NoResultFound`, and extend `_find_one_if_exists()` to try `id` then
  `source_url`. This is the exact shape `ExchangeRateFacade._find_one_if_exists()` already
  uses for `record_date` — copy it rather than inventing a variant. `create_or_update()`
  needs no change once `_find_one_if_exists` knows about `source_url`.
- **`backend/models/exchange_rate/facade.py`** — add
  `get_latest_on_or_before(record_date)` → `Optional[ExchangeRateEntity]`, ordering
  `record_date` descending with `LIMIT 1`. Returns `None` rather than raising; the caller
  branches on it.
- **`backend/_factories/property/db.py`** — add `status = "active"`, plus `amenities`,
  `description`, and `name`, following how `_factories/listing/db.py` fakes the equivalent
  fields. Existing factory callers keep working.

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
  the *"Detalles de la Propiedad"* block, and `description` from the *"Descripción"* block.
  Keep the selectors in one module-level dict so a redesign is a single-place fix.
  **`amenities` and `name` are not recoverable here** — `facilities` is client-rendered, and
  the `<h1>` carries the same auto-generated title tier 1 already reads. Tier 3 leaves
  `amenities` as `[]` and `name` as `None`.
- `amenities` — `[f["name"] for f in d.get("facilities") or []]`, preserving payload order
  and the original Spanish. Drop `group` and `id`; this must stay value-compatible with
  `listings.amenities`. Guard on `facilitiesNotApply` being truthy → `[]`.
- `description` — `d["description"]` stored verbatim. The leading `Código ***` is the site's
  own contact-masking, not scrape noise; do not strip it, or the stored text stops matching
  the page.
- `name` — `d["title"]`.
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

- `PropertyCreateRequest(BaseModel)` — three field groups, which the docstring should spell
  out because the validator is otherwise easy to misread:
  1. `source_url: Optional[str]` — the scrape path.
  2. The manual set (`address`, `city`, `state`, `country`, `bedrooms`, `property_type`,
     `latitude`, `longitude`, `purchase_price_cop`, …) — the off-market path.
  3. **Always-optional overrides: `name`, `notes`, `description`, `amenities`.** These are
     valid alongside *either* path and must be excluded from the XOR check — otherwise
     `{"source_url": ..., "name": "Salento finca #2"}` would be rejected as supplying both.

  A Pydantic v2 `@model_validator(mode="after")` enforces *either* group 1 *or* group 2,
  ignoring group 3 entirely. FastAPI surfaces a violation as a clean 422.
- `PropertyResponse(BaseResponseModel)` with `data: PropertyEntity`, matching
  `api/models/listing.py`.

**`backend/api/routes/properties.py`** — `properties_router = APIRouter(prefix="/api")`,
`logger = init_logging(__file__)`, `API_DB_SessionDependency` for the session. Follow the
try/except/`HTTPException` shape in `api/routes/listings.py`.

`POST /api/properties`:

1. If `source_url` — resolve parser, fetch, parse. `UnsupportedSource` → 400,
   `FetchError` → 502, `ScrapeError` → 422.
2. Else use the manual body directly.
3. Apply the group-3 overrides last, so an explicit `name` beats the scraped `title`:
   `payload["name"] = body.name or scraped.get("name")`, and likewise for `description`
   and `amenities`. Use `is not None` rather than truthiness for `amenities`, so an explicit
   `[]` clears the list instead of silently falling back to the scraped values.
4. Resolve the rate and compute `purchase_price_usd = purchase_price_cop / cop_per_usd`,
   skipping when the price is hidden.
5. `PropertyFacade.create_or_update()` → upserts on `source_url`. Commit. Return 201.

**`backend/api/app/main.py`** — import and `app.include_router(properties_router)`.
`methods` in the CORS middleware already includes `POST`.

### 5. Tests

`services/_tests/test_finca_raiz.py` (with `__init__.py`) — save the real Salento page as an
HTML fixture, then derive three variants from it to exercise each tier: full, `__NEXT_DATA__`
stripped, and both JSON blocks stripped. Assert the exact live values from the table above,
including `amenities == ["Patio", "Servicios Públicos"]` and
`name == "Casa en Venta en Ahitamara, Salento"`.

Assert the tier-3 degradation explicitly: the `__NEXT_DATA__`-stripped variant must still
produce a persistable record, but with `amenities == []` and `name is None`. This is the one
behaviour most likely to be "fixed" into a false positive later, so it needs a test that
states it is intentional.

Cover `facilitiesNotApply` truthy → `[]`, `hidePrice` / `sold` / `active: false` → status,
and a malformed page → `ScrapeError`. Use the existing `http_requests_mock` fixture
(`conftest.py`) — this repo mocks HTTP with `requests-mock`, not `responses`.

`api/_tests/routes/test_routes_properties.py` — follow `test_routes_markets.py`:
`test_app_client`, `test_db_session`, `PropertyDBFactory`, and assert against
`PropertyEntity.model_validate(...).model_dump(mode="json")`. Cover the URL path, the manual
path, the XOR validator rejecting both-or-neither, re-POST of the same URL updating in place
rather than inserting, and the cold-start branch where `exchange_rates` is empty and
frankfurter is called (mock it). Add two cases for the group-3 overrides: `{source_url, name}`
is accepted (not a XOR violation) and the supplied `name` wins over the scraped title; an
explicit `"amenities": []` alongside a `source_url` persists as empty rather than falling
back to the scraped list.

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

Also expect `name: "Casa en Venta en Ahitamara, Salento"`,
`amenities: ["Patio", "Servicios Públicos"]`, and a `description` beginning `"Código ***"`.
An empty `amenities` here means tier 1 silently failed and the parse fell through to the
DOM — check before assuming the listing has no amenities.

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
