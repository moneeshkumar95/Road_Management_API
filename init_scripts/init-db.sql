DO
$do$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'edigital') THEN
      PERFORM dblink_exec('dbname=postgres', 'CREATE DATABASE edigital');
   END IF;
END
$do$;

\c edigital;

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;