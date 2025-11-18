CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS analytics;

-- raw.taxi_zone_lookup
CREATE TABLE IF NOT EXISTS raw.taxi_zone_lookup (
  locationid INTEGER PRIMARY KEY,
  borough TEXT,
  zone TEXT,
  service_zone TEXT,
  ingested_at_utc TIMESTAMP DEFAULT now()
);

-- raw.yellow_taxi_trip
CREATE TABLE IF NOT EXISTS raw.yellow_taxi_trip (
  -- columnas mínimas, conserva los tipos originales
  tpep_pickup_datetime TIMESTAMP,
  tpep_dropoff_datetime TIMESTAMP,
  passenger_count INTEGER,
  trip_distance DOUBLE PRECISION,
  PULocationID INTEGER,
  DoLocationID INTEGER,
  fare_amount DOUBLE PRECISION,
  extra DOUBLE PRECISION,
  mta_tax DOUBLE PRECISION,
  tip_amount DOUBLE PRECISION,
  tolls_amount DOUBLE PRECISION,
  improvement_surcharge DOUBLE PRECISION,
  congestion_surcharge DOUBLE PRECISION,
  airport_fee DOUBLE PRECISION,
  total_amount DOUBLE PRECISION,
  RatecodeID INTEGER,
  payment_type INTEGER,
  VendorID INTEGER,
  store_and_fwd_flag TEXT,
  source_year INTEGER,
  source_month INTEGER,
  ingested_at_utc TIMESTAMP DEFAULT now(),
  source_path TEXT,
  run_id TEXT,
  service_type TEXT,
  PRIMARY KEY (
    tpep_pickup_datetime,
    tpep_dropoff_datetime,
    PULocationID,
    DoLocationID,
    VendorID
  )
);

-- raw.green_taxi_trip
CREATE TABLE IF NOT EXISTS raw.green_taxi_trip (
  lpep_pickup_datetime TIMESTAMP,
  lpep_dropoff_datetime TIMESTAMP,
  passenger_count INTEGER,
  trip_distance DOUBLE PRECISION,
  PULocationID INTEGER,
  DoLocationID INTEGER,
  fare_amount DOUBLE PRECISION,
  extra DOUBLE PRECISION,
  mta_tax DOUBLE PRECISION,
  tip_amount DOUBLE PRECISION,
  tolls_amount DOUBLE PRECISION,
  improvement_surcharge DOUBLE PRECISION,
  congestion_surcharge DOUBLE PRECISION,
  airport_fee DOUBLE PRECISION,
  total_amount DOUBLE PRECISION,
  RatecodeID INTEGER,
  payment_type INTEGER,
  VendorID INTEGER,
  store_and_fwd_flag TEXT,
  source_year INTEGER,
  source_month INTEGER,
  ingested_at_utc TIMESTAMP DEFAULT now(),
  source_path TEXT,
  run_id TEXT,
  service_type TEXT,
  PRIMARY KEY (
    lpep_pickup_datetime,
    lpep_dropoff_datetime,
    PULocationID,
    DoLocationID,
    VendorID
  )
);