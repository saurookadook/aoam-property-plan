# Pending market captures

The four markets on the Phase 4 roster that have no `/markets/summary` capture yet:
**Cali, Cartagena, Medellín, Santa Marta**. Only Salento, Calima, Pance and Bogota are seeded
(finding 1 in `doc/planning/PHASE_4_REACT_DASHBOARD.md`).

Each file here is a summary capture with the market tuple filled in and **every figure `null`**.
They live in this subdirectory rather than in `seed_data/` because `seed_markets.py` globs
`seed_data/*.json` non-recursively — a placeholder sitting next to the real captures would be
seeded as a market with no ADR and no occupancy, and both columns are `NOT NULL`. `seed_markets.py`
also skips any capture whose figures are missing, so moving one up half-filled fails loudly
rather than writing a market that reads as real.

## Activating one

1. **Verify the tuple.** `_tuple_verified` says whether the country/region/locality strings are
   known to match. Only Cali's are — every `_research/markets/search/*__search.json` capture
   returns it. For the other three, call `POST /markets/search` and commit the response to
   `_research/markets/search/` the way the existing captures got there. `airroi._market_body`
   sends a three-part tuple and a miss returns nothing rather than an error, so an unverified
   guess seeds a market that will never get figures.
2. **Capture the summary.** `services.airroi.get_market_summary` against the verified tuple.
   Commit the raw response to `_research/markets/summary/`, matching
   `{calima,pance,salento}_*__summary.json`.
3. **Fill the file in** from that response, drop the `_tuple_*` and `_todo` keys, and move it up
   into `seed_data/`.
4. **Re-run** `seed_markets.py`. It refreshes an existing report now rather than skipping the
   market, so this is safe to repeat.
5. **Ingest the rest**: `manual_run markets_summaries` → `listings_by_market` →
   `markets_peak_months`, in that order. Peak months needs both of the others — it averages the
   ingested listings into a centroid and asks `/calculator/estimate` about that point.
6. **Add properties.** `seed_data/properties/finca_raiz_listings.json` carries an empty group for
   each of these four markets. Three real listings per market is the threshold below which the
   budget indicator hides itself.

## Note on Cali

Cali is on the roster because AirROI has no _Granada_ and no _El Peñón_ — both search terms
resolve to Cali (4,690 listings). It carries the Granada / El Peñón thesis, and the market
overview is meant to show a display note saying so.
