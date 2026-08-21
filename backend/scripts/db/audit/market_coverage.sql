-- Chunk 1 acceptance evidence: does every market have a report, and does that
-- report have figures?
--
-- Run before touching anything and again after
--   markets_summaries -> listings_by_market -> markets_peak_months
-- and diff the two. A market with a NULL last_updated has never been summarised;
-- a market with NULL peak_months / monthly_revenue_distribution has been
-- summarised but has no ingested listings to build a centroid from, which is
-- markets_peak_months silently skipping it.
--
--   ./scripts/admin.sh ...   or, directly:
--   docker compose exec pg_database psql -U postgres -d aoam_property_plan \
--     -f /opt/scripts/db/audit/market_coverage.sql
--
-- LEFT JOIN LATERAL rather than a plain LEFT JOIN: handle_markets_summaries
-- inserts a fresh row per run, so a market accumulates a history and only the
-- latest of them is "the report". Ordered the same way
-- MarketFinancialReportFacade.get_latest_by_market_id orders, so this reports
-- the row the application would read.
SELECT
    m.locality,
    m.region,
    mfr.adr_cop,
    mfr.occupancy_rate,
    mfr.annual_revenue_cop,
    mfr.listing_count            AS airroi_listing_count,
    mfr.peak_months,
    cardinality(mfr.monthly_revenue_distribution) AS distribution_months,
    ingested.listing_count       AS ingested_listing_count,
    ingested.latitude            AS centroid_latitude,
    ingested.longitude           AS centroid_longitude,
    mfr.last_updated
FROM markets m
LEFT JOIN LATERAL (
    SELECT *
    FROM market_financial_reports r
    WHERE r.market_id = m.id
    ORDER BY r.last_updated DESC, r.created_at DESC
    LIMIT 1
) mfr ON true
-- The same AVG that MarketFacade._centroid_select computes, so the audit and the
-- read path agree on where a market is and on how much of it we hold.
LEFT JOIN LATERAL (
    SELECT
        count(l.id)      AS listing_count,
        avg(l.latitude)  AS latitude,
        avg(l.longitude) AS longitude
    FROM listings l
    WHERE l.market_id = m.id
) ingested ON true
ORDER BY m.locality;
