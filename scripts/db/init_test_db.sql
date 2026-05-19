DROP DATABASE IF EXISTS test_aoam_property_plan;


CREATE DATABASE test_aoam_property_plan ENCODING 'UTF8';

DO $body$
BEGIN
    IF NOT EXISTS (
        SELECT *
        FROM pg_user
        WHERE usename = 'app')
        THEN
        CREATE USER app WITH INHERIT LOGIN PASSWORD 'app';
    END IF;
END
$body$;

GRANT ALL ON SCHEMA public TO app;


\connect test_aoam_property_plan;

CREATE EXTENSION IF NOT EXISTS postgis;
-- NOTE: Maybe needed?
-- CREATE EXTENSION postgis_raster;
-- CREATE EXTENSION postgis_sfcgal;
-- CREATE EXTENSION fuzzystrmatch; --needed for postgis_tiger_geocoder
-- --optional used by postgis_tiger_geocoder, or can be used standalone
-- CREATE EXTENSION address_standardizer;
-- CREATE EXTENSION address_standardizer_data_us;
-- CREATE EXTENSION postgis_tiger_geocoder;
-- CREATE EXTENSION postgis_topology;
