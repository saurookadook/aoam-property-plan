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

