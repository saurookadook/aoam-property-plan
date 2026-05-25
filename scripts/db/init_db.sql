SELECT
    'CREATE DATABASE aoam_property_plan'
WHERE
    NOT EXISTS (
        SELECT
        FROM
            pg_database
        WHERE
            datname = 'aoam_property_plan') \gexec


DO $body$
BEGIN
    IF NOT EXISTS (
        SELECT
            *
        FROM
            pg_user
        WHERE
            usename = 'app') THEN
        CREATE USER app WITH INHERIT LOGIN PASSWORD 'app';
    END IF;

    IF NOT EXISTS (
        SELECT
            *
        FROM
            pg_user
        WHERE
            usename = 'migrations') THEN
        CREATE USER migrations WITH INHERIT LOGIN PASSWORD 'migrations';
    END IF;
END
$body$;


\connect aoam_property_plan;


ALTER DEFAULT PRIVILEGES GRANT USAGE ON SCHEMAS TO PUBLIC;


ALTER DEFAULT PRIVILEGES
FOR ROLE migrations GRANT
SELECT ON TABLES TO PUBLIC;


GRANT ALL ON SCHEMA public TO migrations;


REVOKE CREATE ON SCHEMA public FROM app;


ALTER DEFAULT PRIVILEGES
FOR ROLE migrations GRANT ALL ON TYPES TO app;


ALTER DEFAULT PRIVILEGES
FOR ROLE migrations GRANT ALL ON SEQUENCES TO app;


ALTER DEFAULT PRIVILEGES
FOR ROLE migrations GRANT INSERT, UPDATE, DELETE,
REFERENCES ON TABLES TO app;


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
