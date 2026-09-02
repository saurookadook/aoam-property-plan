**COLOMBIA**  
**Short-Term Rental Market Research System**

*Engineering Execution Plan  —  Powered by AirROI API*

Bogota  ·  Cali (Granada, El Peñon, Calima, Pance)  ·  Salento  ·  Cartagena  ·  Medellin  ·  Santa Marta

| Item | Detail |
| :---- | :---- |
| **Pre-approval budget** | COP $1,766,000,000  (≈ USD $425,600 at COP 4,150/USD) |
| **Target markets** | Bogota (Chapinero, Usaquen)  ·  Cali (Granada, El Peñon, Calima, Pance)  ·  Salento  ·  Cartagena  ·  Medellin  ·  Santa Marta |
| **Primary STR data** | AirROI API  —  22 REST endpoints, $0.01/call, no contract, instant key |
| **Property prices** | Finca Raiz scraper (COP asking prices) |
| **Backend** | Python 3.11+  \+  FastAPI  \+  Pydantic v2 |
| **Frontend** | React 18  \+  TypeScript  \+  Vite |
| **Database** | PostgreSQL 16  \+  PostGIS extension |
| **Hosting (MVP)** | Railway (backend \+ DB \+ cron)  \+  Vercel (frontend) |
| **Est. monthly running cost** | \~$30–$75 USD at MVP scale  vs  $300–$500/month for AirDNA |

# **Part 1 — Budget Analysis & Market Fit**

**Your pre-approval of COP $1,766,000,000** (≈ USD $425,600) is a substantial budget that opens quality STR-grade properties across most Colombian markets. However, purchasing power varies significantly by city — it buys 1 apartment in Cartagena or 4–5 fincas in Calima. The table below ranks all 8 markets by investment fit, defined as the combination of price-to-revenue ratio, how many properties your budget can purchase, occupancy reliability, and regulatory risk.

**Cali market expanded:** This version expands the Cali analysis to include Calima (Lake Calima / Daríen) and Pance — two rural sub-markets within Valle del Cauca that offer meaningfully higher ADR and lower purchase prices than urban Cali apartments, with no HOA restrictions on standalone properties.

| Market | ADR (USD) | Occupancy | Est. annual revenue | Avg. price range (COP) | Units at budget | Fit & rationale |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **Cali region — expanded (ranked by investment fit)** |  |  |  |  |  |  |
| **Calima (Lake Calima)** Valle del Cauca — lake & watersports | $65–$120 | 55–70% | \~$16K–$22K | COP 280–500M Fincas & lake houses | **3–5 units** Highest portfolio count | **Strong fit** Highest ADR vs. price in the region. Watersports tourism (kitesurfing, windsurfing) drives consistent weekend demand. Lowest prices \= most units per peso. Emerging — low competition. |
| **Pance** Southern Cali — nature retreat | $60–$95 | 55–65% | \~$13.5K–$18K | COP 450–700M Cabins & retreats | **2–3 units** City \+ nature combo | **Strong fit** 30 min from Cali center. Luxury cabins with Farallones views command premium rates. No HOA or building committee restrictions on standalone properties. |
| **Salento** Quindio — Coffee Region | $55–$75 | 60–70% | \~$14.6K–$19.2K | COP 350–600M Fincas & townhouses | **3–4 units** Best occupancy rate | **Strong fit** Coffee Region tourism drives year-round international demand. Highest sustained occupancy of all markets. No HOA on most finca-style properties. Minimal regulatory risk. |
| **Cali — Granada & El Peñon** Urban Cali — nightlife & culture | $30–$46 | 40–53% | \~$7.6K–$9.2K | COP 500–750M STR apartments | **2–3 units** Urban diversification | **Good fit** Lower ADR but strong urban demand. World Salsa Festival (June) spikes rates 30–50%. Less saturated than Bogota or Medellin. Gross yields 6–8% achievable. |
| **Other target markets** |  |  |  |  |  |  |
| **Bogota** Chapinero & Usaquen | $34–$73 | 53–60% | \~$9.2K–$14.6K | COP 700M–1.1B STR apartments | **1–2 units** Capital city liquidity | **Good fit** Largest STR market in Colombia (22,000+ listings). Year-round corporate \+ tourism demand. HOA COP 400K–1.2M/month is a significant cost. RNT enforcement tightening in 2026\. |
| **Medellin** Laureles & El Poblado | $33–$85 | 55–65% | \~$10.8K–$15.6K | COP 750M–1.1B STR apartments | **1–2 units** Highest ADR ceiling | **Good fit** Best occupancy of urban markets (63% median). El Poblado is heavily saturated — top performers drive the averages. High regulation (88% licensed). Budget buys 1–2 units only. |
| **Santa Marta** Magdalena — Caribbean beach | $44–$89 | 32–45% | \~$7.9K–$11K | COP 500–800M Beach apartments | **2 units** High seasonal risk | **Moderate fit** High ADR ceiling but lowest occupancy (32% average). Supply grew 114% YoY — very competitive. Highly seasonal: strong Jan–Mar, very soft May–Sep. Best as a secondary market. |
| **Cartagena** Getsemani & Centro Hist. | $65–$96+ | 47–57% | \~$18,036 | COP 1.0–1.4B Premium STR units | **1 unit** Zero diversification | **Use caution** Highest revenue per property but budget buys exactly 1 unit with no reserve. If that unit has vacancy or maintenance issues, all income stops. Consider after building cash flow elsewhere. |

Note: Est. annual revenue \= median ADR × projected occupancy × 365\. Price ranges reflect STR-grade properties in prime STR sub-neighborhoods. “Units at budget” assumes all-cash purchase at price range midpoint. Data sourced from AirROI, TheLatinvestor, and GlobalPropertyGuide (2025–2026).

## **1.1  Recommended portfolio strategies**

| Strategy | Allocation | Est. properties | Why it works |
| :---- | :---- | :---- | :---- |
| **Diversified — rural \+ nature** | 2 Calima \+ 2 Salento \+ 1 Pance | 5 properties (\~COP 1.6B) | Maximum portfolio count. All 3 markets have strong occupancy, low purchase prices, and zero HOA costs. Geographic spread reduces risk. Best use of the full budget. |
| **Balanced — rural \+ urban** | 1 Bogota \+ 1 Salento \+ 1 Pance | 3 properties (\~COP 1.65B) | Mixes stable year-round urban income (Bogota corporate demand) with high-occupancy rural units. Diversifies guest types and seasonal risk. |
| **Concentrated — Cartagena only** | 1 prime Cartagena unit | 1 property (\~COP 1.2–1.4B) | Highest single-property revenue ceiling but zero diversification. Recommended only after validating operations in lower-risk markets first. |

**Recommendation:** Start with Calima or Salento. Both markets give you 3+ properties for your budget, have the strongest occupancy-to-price ratios, and carry the lowest regulatory risk. Use the research system to validate 3–5 specific listings before committing capital.

# **Part 2 — How Each Metric Is Sourced and Calculated**

Every metric surfaces from one of three sources: the AirROI API, the Finca Raiz scraper, or a formula your calculation engine computes from those inputs. This table defines the exact method for each of the 9 metrics the system produces.

| Metric | Data source | AirROI endpoint | How it’s calculated |
| :---- | :---- | :---- | :---- |
| **Avg Daily Rate (ADR)** | AirROI | /markets/summary/listings/search/radius | Median booked nightly rate for comparable listings in target area, filtered by bedroom count and property type. Use trailing 12-month window. |
| **Projected Occupancy** | AirROI | /markets/occupancy/listings/metrics/all | Booked nights ÷ available nights from listing calendar data, averaged across comparable properties over trailing 12 months. |
| **Projected Annual Revenue** | AirROI \+ Calc | /markets/revenueRevenue Calculator | ADR × Projected Occupancy × 365\. AirROI’s Revenue Calculator endpoint returns this directly per address or market. Cross-check with the manual formula and surface both figures. |
| **Peak Months** | AirROI | /markets/seasonality | Months where ADR or occupancy exceeds the annual average by 15%+. AirROI returns monthly breakdowns. Flag top 3 months. Feeds the seasonal forecast calendar view. |
| **Purchase Price** | Finca Raiz scraper | fincaraiz.com.co listing pages | Scraped from the Finca Raiz listing URL (asking price in COP). Also accepts manual entry for off-market properties. Converted to USD at daily exchange rate. |
| **Monthly Expenses** | Manual input \+ formula | No API — user-defined | Fixed: mortgage payment (from purchase price, down %, rate, term) \+ predial \+ HOA. Variable: property management fee (18–25% of revenue) \+ maintenance reserve (1% of purchase price ÷ 12). |
| **Cash on Cash Return** | Calc engine | Derived metric | Annual Net Income ÷ Total Cash Invested. Net Income \= Annual Revenue − Annual Expenses. Cash Invested \= down payment \+ closing costs (2.5–3%) \+ renovation budget. |
| **Payback Period** | Calc engine | Derived metric | Total Cash Invested ÷ Annual Net Income. Returned in years as a float. Flag any property above 12 years as low priority. |
| **Comparable Listings** | AirROI | /listings/comparables | Pass target property lat/lng \+ bedrooms \+ property type. Returns 10–20 nearest similar active listings with ADR, occupancy, revenue, and distance. Displayed as a sortable table. |

# **Part 3 — Phased Execution Plan**

Four phases, each ending with a working deliverable. The engineer starts today on Phase 1 and should have live market data in the database by end of day.

  **PHASE 1     AirROI Integration & Database Setup**

Duration: Day 1–3  |  Deliverable: Verified STR market data for all 8 target markets flowing into PostgreSQL.

| Step 1   Sign up for AirROI and validate coverage for all 8 markets |
| :---- |
| Go to airroi.com, create a free account, and add $10 in API credits (instant activation). |
| Retrieve the API key from the developer dashboard. |
| Run a test call to /markets/search for: Bogota, Cali, Salento, Cartagena, Medellin, Santa Marta, Calima (try "Calima, Valle del Cauca" and "Lago Calima"), and Pance. |
| For each market: record whether ADR, occupancy, and revenue fields are populated and how many active listings are returned. |
| Calima and Pance may have thin coverage in AirROI as standalone markets — if fewer than 30 listings return, fall back to searching the broader "Darien, Valle del Cauca" or "Sur de Cali" market and filtering by proximity. |
| Save the raw JSON response for each market to a local file for schema reference before writing any database code. |

| Step 2   Set up PostgreSQL 16 with PostGIS |
| :---- |
| Install PostgreSQL 16 locally or spin up a free instance on Railway or Neon.tech. |
| Enable the PostGIS extension: CREATE EXTENSION postgis; |
| markets table: id, city, neighborhood, country, adr\_usd, occupancy\_rate, annual\_revenue\_usd, peak\_months TEXT\[\], listing\_count, last\_updated. |
| listings table: airroi\_id, market\_id FK, lat, lng, location GEOGRAPHY(Point,4326), bedrooms, property\_type, adr\_usd, occupancy\_rate, annual\_revenue\_usd, source\_url. |
| properties table: id, address, lat, lng, bedrooms, property\_type, purchase\_price\_cop BIGINT, purchase\_price\_usd NUMERIC, source\_url, notes, created\_at. |
| property\_financial\_reports table: id, property\_id FK, down\_payment\_pct, interest\_rate, loan\_term\_years, monthly\_expenses\_usd, annual\_revenue\_usd, annual\_net\_income\_usd, cash\_invested\_usd, coc\_return\_pct, payback\_years NUMERIC, exchange\_rate, calculated\_at. |
| exchange\_rates table: date DATE PRIMARY KEY, cop\_per\_usd NUMERIC. Populated daily from a free API. |
| Create a GiST index on listings.location to support fast radius queries: CREATE INDEX idx\_listings\_location ON listings USING GIST(location); |

| Step 3   Build AirROI data ingestion scripts (Python) |
| :---- |
| ingest\_markets.py: Calls /markets/summary for all 8 target markets. Writes ADR, occupancy, revenue, and peak months to the markets table. Run once now; schedule nightly. |
| ingest\_listings.py: Calls /listings/search/market for each market with pagination. Writes results to the listings table. Filter for 1–3 bedroom apartments, houses, and fincas. |
| ingest\_exchange\_rate.py: Fetches COP/USD rate from frankfurter.app (free, no API key). Writes to exchange\_rates. Schedule daily at 9am Colombia time (UTC-5). |
| Run all three scripts and confirm data is present in the database before moving to Phase 2\. |

  **PHASE 2     Finca Raiz Scraper & Calculation Engine**

Duration: Day 3–6  |  Deliverable: Any candidate property address returns a complete financial projection in JSON.

| Step 4   Build the Finca Raiz price scraper |
| :---- |
| Write a lightweight Python scraper using httpx \+ BeautifulSoup targeting fincaraiz.com.co. |
| Input: a Finca Raiz listing URL. Output: asking price in COP, neighborhood, bedrooms, property type. |
| Apply the daily COP/USD rate from the exchange\_rates table to convert and store both values in the properties table. |
| This scraper runs on-demand only when a user adds a new property — not on a schedule. |
| Also implement a manual entry fallback: accept price directly as a POST body parameter for off-market or private sale properties. |
| For Calima and Pance properties, also check fincainca.com and metrocuadrado.com as alternative listing sources if Finca Raiz coverage is thin. |

| Step 5   Build the financial calculation module (calculations.py) |
| :---- |
| mortgage\_payment(purchase\_price\_usd, down\_pct, annual\_rate, term\_years): standard amortization formula, returns monthly payment in USD. |
| monthly\_expenses(mortgage, hoa\_usd, mgmt\_fee\_pct, annual\_revenue\_usd, property\_value\_usd): sums mortgage \+ HOA \+ management fee \+ maintenance reserve (1% of value ÷ 12). |
| annual\_net\_income(annual\_revenue\_usd, monthly\_expenses\_usd): annual revenue minus annualized expenses. |
| coc\_return(annual\_net\_income\_usd, cash\_invested\_usd): returns percentage. |
| payback\_period(cash\_invested\_usd, annual\_net\_income\_usd): returns years as a float. |
| closing\_costs(purchase\_price\_usd): returns 2.75% as the default Colombia estimate (notary \+ registration \+ taxes). |
| All functions take explicit parameters only — no global state. Unit-test each with known inputs before connecting to the API. |
| Colombian defaults to pre-load in the UI: 10% interest rate, 30% down, 15-year term, 22% management fee, COP 0 HOA for fincas, COP 350,000 HOA for urban apartments. |

| Step 6   Wire AirROI revenue data into the calculation engine |
| :---- |
| For any candidate property: (1) call /listings/comparables with the property’s lat/lng \+ bedrooms \+ property type, (2) compute median ADR and median occupancy across the comp set, (3) calculate projected annual revenue as median\_adr × median\_occupancy × 365\. |
| Also call AirROI’s Revenue Calculator endpoint and surface both figures — the direct AirROI estimate and the comp-derived estimate. Mark the lower of the two as the "conservative" figure. |
| Write the full result to the financials table with a calculated\_at timestamp. |
| Write the comp listings used to a property\_comps table linking property\_id to listing airroi\_id, so comps can be retrieved later without a repeat API call. |

  **PHASE 3     FastAPI Backend**

Duration: Day 6–9  |  Deliverable: A fully documented REST API serving all market and property data. Testable via Swagger UI at /docs.

| Step 7   Project structure and dependencies |
| :---- |
| Install: pip install fastapi uvicorn asyncpg sqlalchemy pydantic httpx beautifulsoup4 python-dotenv |
| Project layout: /app/main.py, /app/routers/ (markets.py, properties.py, comps.py), /app/services/ (airroi.py, calculations.py, finca\_raiz.py, exchange\_rate.py), /app/models/ (database.py, schemas.py). |
| Define all Pydantic v2 response models in schemas.py matching exactly what each endpoint returns. Strict TypeScript types on the frontend are derived from these. |
| Store AirROI API key, database URL, and exchange rate API URL in a .env file. Never hardcode credentials. |

| Step 8   Define all API endpoints |
| :---- |
| GET /markets — returns all 8 markets with ADR, occupancy, annual revenue, peak months, listing count, and last\_updated. |
| GET /markets/{city}/listings — returns top 50 listings for a city. Accepts bedrooms and property\_type query params. Sortable by revenue or occupancy. |
| POST /properties — accepts Finca Raiz URL or manual inputs. Triggers the scraper. Returns the saved property object with both COP and USD price. |
| POST /properties/{id}/analyze — accepts expense inputs (down\_payment\_pct, interest\_rate, hoa\_cop, mgmt\_fee\_pct, renovation\_cop). Runs the calculation engine. Writes and returns the financials JSON. |
| GET /properties/{id}/comps — calls AirROI /listings/comparables. Returns the comp table with 10–20 listings including ADR, occupancy, revenue, and distance in km. |
| GET /properties/{id}/comps/cached — returns comps from the property\_comps table without a new API call (free after first analysis). |
| GET /exchange-rate — returns the current COP/USD rate and the date it was fetched. |
| All amounts stored and returned in both COP and USD. All Pydantic response models explicitly typed. |

| Step 9   Validate end-to-end with a real Salento or Calima property |
| :---- |
| Find a live Finca Raiz listing in Salento or Calima. |
| POST the URL to /properties — confirm the scraper returns the correct price in COP. |
| POST to /properties/{id}/analyze with Colombian default expense inputs. |
| Verify the JSON contains all 9 metrics: ADR (both estimate methods), occupancy, projected revenue, peak months, purchase price (COP \+ USD), monthly expenses, CoC return, payback period. |
| GET /properties/{id}/comps — confirm at least 5 comparable listings are returned with distances. |
| Fix any data quality or schema issues before building the frontend. |

  **PHASE 4     React \+ TypeScript Dashboard**

Duration: Day 9–14  |  Deliverable: A deployed React dashboard for evaluating all 8 markets and individual properties.

| Step 10   Project setup (React \+ TypeScript) |
| :---- |
| Scaffold: npm create vite@latest colombia-str \-- \--template react-ts |
| Install: react-query (data fetching \+ caching), react-router-dom v6, axios, recharts (charts), react-leaflet \+ leaflet (Colombia map), @types/leaflet. |
| Create /src/types/api.ts with TypeScript interfaces matching every FastAPI Pydantic schema. Use these types throughout — never use "any". |
| Configure a .env file with VITE\_API\_URL pointing to the FastAPI backend. |
| Set up react-query QueryClient with 1-hour stale time for market data and 30-minute stale time for property comps. |

| Step 11   Market overview screen |
| :---- |
| Route: / (home) |
| React-Leaflet map of Colombia centered on the 8 target markets. Click a city marker to scroll to its card. |
| Grid of 8 market cards below the map. Each card shows: city, ADR (USD), projected occupancy %, projected annual revenue (USD), peak months as colored pills, active listing count. |
| Budget indicator on each card: given COP $1,766,000,000, show "Estimated properties purchasable: X" based on the market’s average property price. |
| Sort cards by investment fit score by default. Allow re-sort by ADR, occupancy, or annual revenue. |
| Data from GET /markets via react-query. |

| Step 12   Property deep-dive screen |
| :---- |
| Route: /analyze |
| Input form (React state, not HTML form element): Finca Raiz URL or manual address, down payment % (default 30%), interest rate % (default 10%), HOA in COP (default 0 for rural, 350,000 for urban), management fee % (default 22%), renovation budget COP (optional). |
| On submit: POST to /properties then POST to /properties/{id}/analyze. Show skeleton loading cards during API calls. |
| Results panel: 9 metric cards in a 3×3 grid. ADR, occupancy, and projected revenue at top. Monthly expenses, annual net income, cash invested in the middle. CoC return and payback period at bottom — color-coded green (CoC \> 8%), amber (5–8%), red (\< 5%). |
| Revenue comparison row: AirROI direct estimate vs. comp-derived estimate side by side. Label the lower as "conservative". |
| Sensitivity table: 3×3 grid of CoC return at ADR \-10%/base/+10% vs occupancy \-10%/base/+10%. Computed in TypeScript from base figures — no API call. |
| Peak months: 12-bar Recharts BarChart showing relative occupancy by month from seasonality data. |
| Currency toggle: all monetary values switch between USD and COP on one click, using the rate from GET /exchange-rate. |

| Step 13   Comparable listings panel |
| :---- |
| Rendered below the financials on the deep-dive screen. |
| Sortable table: address, property type, bedrooms, ADR (USD), occupancy %, est. annual revenue (USD), distance from target property in km. |
| Default sort: annual revenue descending. |
| Each row links to the Airbnb listing URL where available. |
| Data from GET /properties/{id}/comps/cached (first call fetches live; subsequent calls use the cached version). |
| Show a "Refresh comps" button that triggers a fresh call to GET /properties/{id}/comps. |

| Step 14   Deploy |
| :---- |
| Backend: push to GitHub. Connect Railway to the repo — Railway auto-detects Python and runs uvicorn main:app. Add the Railway PostgreSQL plugin. Set nightly ingest scripts as Railway Cron Jobs. |
| Frontend: connect the same or a separate repo to Vercel. Set VITE\_API\_URL to the Railway backend URL in Vercel environment variables. Automatic deploy on push to main. |
| Test the full flow from the deployed URL: add a Salento listing, run the analysis, verify all 9 metrics render, confirm comps load and the currency toggle works. |
| Share the URL with the team. The system is now live for market research. |

# **Part 4 — What to Do Today**

Six tasks to complete before end of day. These establish the foundation everything else builds on.

| \# | Task | Acceptance criteria |
| :---- | :---- | :---- |
| **1** | AirROI account | Sign up at airroi.com. API key visible in dashboard. $10 in credits added. |
| **2** | Coverage check | API returns market data (ADR \+ occupancy populated) for all 8 markets. Calima and Pance alternatives identified if coverage is thin. Raw JSON saved locally. |
| **3** | PostgreSQL running | PostgreSQL 16 running locally or on Railway. PostGIS enabled. All 5 tables created with correct schema. GiST index on listings.location confirmed. |
| **4** | Markets ingested | ingest\_markets.py runs without error. All 8 markets have rows in the markets table with ADR and occupancy values present. |
| **5** | Calc functions | calculations.py exists with all 6 functions. Manual test with known inputs returns correct values. Example: COP 500M Calima finca at 30% down, 10% rate, 15 years, 0 HOA \= \~USD 1,540/month mortgage. |
| **6** | Finca Raiz scrape | Scraper returns correct price in COP from a live Salento or Calima listing URL. Converts to USD using frankfurter.app. |

# **Part 5 — Tech Stack Reference**

| Layer | Technology | Notes |
| :---- | :---- | :---- |
| **Data ingestion** | Python 3.11 \+ httpx \+ BeautifulSoup | AirROI API calls \+ Finca Raiz scraper \+ exchange rate fetch. Use httpx async for concurrent market ingestion. |
| **Job scheduling** | Railway Cron (MVP) / Celery \+ Redis (scale) | Nightly market refresh at 3am Colombia time (UTC-5). On-demand scraping triggered by POST /properties calls. |
| **Database** | PostgreSQL 16 \+ PostGIS | PostGIS GEOGRAPHY type for radius-based comp queries. GiST index on listings.location. Use asyncpg driver for async FastAPI routes. |
| **Backend** | Python \+ FastAPI \+ Pydantic v2 | Pydantic v2 for response schemas. SQLAlchemy 2.0 async ORM or raw asyncpg. Swagger UI auto-generated at /docs. CORS configured for the Vercel frontend URL. |
| **Frontend** | React 18 \+ TypeScript \+ Vite | react-query for data fetching and caching. recharts for financial charts. react-leaflet for the Colombia map. Strict TypeScript mode throughout. |
| **Hosting** | Railway (backend) \+ Vercel (frontend) | Railway: auto-deploy from GitHub, built-in PostgreSQL plugin, cron jobs. Vercel: auto-deploy, CDN, free tier sufficient for MVP. |
| **Exchange rate** | frankfurter.app (free, no API key) | GET https://api.frankfurter.app/latest?from=USD\&to=COP. Refresh daily. Store in exchange\_rates table to avoid repeat calls. |
| **STR data** | AirROI API | 22 REST endpoints. Market summary, occupancy, seasonality, listing search (market, radius, polygon), revenue calculator, comparables, future rates. $0.01/call, pay-as-you-go. |

# **Part 6 — Colombia Operating Assumptions**

Use these as default values in the calculation engine. All are editable by the user in the property analysis form.

| Input | Default value | Notes |
| :---- | :---- | :---- |
| Mortgage interest rate | **10.0%** | Midpoint of typical 9–12% COP-denominated loans for foreign buyers. Colombia policy rate: 9.25% as of Jan 2026\. |
| Down payment | **30%** | Conservative assumption. Some banks accept 20% for STR investment properties. |
| Loan term | **15 years** | Standard for investment properties in Colombia. |
| Property management fee | **22% of gross revenue** | Typical range 18–25% for STR management in Colombia. Includes cleaning coordination. |
| Maintenance reserve | **1% of purchase price / year** | Standard industry reserve. Divide by 12 for monthly figure. |
| Closing costs | **2.75% of purchase price** | Notary fees, registration taxes, escritura. Typical range 2.5–3% in Colombia. |
| Predial (property tax) | **0.8% of assessed value / year** | Ranges 0.5–1.5% depending on city and property value. Urban properties (Bogota) toward the higher end. |
| HOA (administración) — urban apartments | **COP 350,000 / month** | COP 200K–1.2M range in urban buildings. Pre-populate based on city: Bogota/Medellin \= COP 500K, Cali urban \= COP 300K. |
| HOA — Calima / Pance / Salento fincas | **COP 0 / month** | Standalone fincas and rural houses have no HOA. This is a significant cost advantage over urban apartments. |
| RNT registration | **Required in all 8 markets** | All markets require Registro Nacional de Turismo registration under 2026 enforcement rules. Free to register at Confecamaras. One-time setup. |
| Currency display | **Both COP and USD** | Store all values in both currencies. Use a daily COP/USD rate refreshed from frankfurter.app. Display a toggle in the UI for switching between the two. |

# **Part 7 — Estimated Running Costs**

| Item | Est. monthly cost | Notes |
| :---- | :---- | :---- |
| AirROI API — market ingestion (8 markets, nightly) | \~$15–$30 | 8 markets × 30 days × \~$0.01/call for summary endpoints. |
| AirROI API — comps \+ property analysis (50/month) | \~$10–$25 | Comparables and revenue calculator calls per property analyzed. |
| Finca Raiz scraper | $0 | Low volume, on-demand only. No proxies needed at this scale. |
| Railway (backend \+ database \+ cron) | $5–$20 | Starter plan covers MVP. Includes PostgreSQL plugin and cron scheduler. |
| Vercel (frontend) | $0 | Free tier is more than sufficient for this workload. |
| frankfurter.app (exchange rate) | $0 | Free, no API key required. |
| **Total MVP running cost** | **\~$30–$75 / month** | Compared to AirDNA at $300–$500/month for equivalent data coverage. |

**Next step after today:**  Once the AirROI coverage check confirms usable data for Calima and Salento (Step 1), run the full data ingestion for those two markets first and complete an end-to-end financial analysis on 3–5 real property listings using COP $1,766,000,000 as the purchase ceiling. This produces the first real investment signal from the system within 3 days.