#!/usr/bin/env python3
import argparse
import os
import psycopg2
from datetime import datetime


class OBTBuilder:
    def __init__(self, db_params):
        self.db_params = db_params
        self.conn = None
    
    def connect(self):
        self.conn = psycopg2.connect(**self.db_params)
        print("Conectado a PostgreSQL")
    
    def disconnect(self):
        if self.conn:
            self.conn.close()
        print("Conexión cerrada")
    
    def create_obt_table(self):
        with self.conn.cursor() as cursor:
            cursor.execute("CREATE SCHEMA IF NOT EXISTS analytics;")
            
            cursor.execute("DROP TABLE IF EXISTS analytics.obt_trips;")
            
            cursor.execute("""
                CREATE TABLE analytics.obt_trips (
                    pickup_datetime TIMESTAMP,
                    dropoff_datetime TIMESTAMP,
                    pickup_hour INTEGER,
                    pickup_dow INTEGER,
                    month INTEGER,
                    year INTEGER,
                    
                    pu_location_id INTEGER,
                    pu_zone VARCHAR(100),
                    pu_borough VARCHAR(50),
                    do_location_id INTEGER,
                    do_zone VARCHAR(100),
                    do_borough VARCHAR(50),
                    
                    service_type VARCHAR(10),
                    vendor_id INTEGER,
                    vendor_name VARCHAR(50),
                    rate_code_id INTEGER,
                    rate_code_desc VARCHAR(50),
                    payment_type INTEGER,
                    payment_type_desc VARCHAR(50),
                    trip_type VARCHAR(10),
                    
                    passenger_count INTEGER,
                    trip_distance DECIMAL(10,2),
                    fare_amount DECIMAL(10,2),
                    extra DECIMAL(10,2),
                    mta_tax DECIMAL(10,2),
                    tip_amount DECIMAL(10,2),
                    tolls_amount DECIMAL(10,2),
                    improvement_surcharge DECIMAL(10,2),
                    congestion_surcharge DECIMAL(10,2),
                    airport_fee DECIMAL(10,2),
                    total_amount DECIMAL(10,2),
                    store_and_fwd_flag VARCHAR(1),
                    
                    trip_duration_min DECIMAL(10,2),
                    avg_speed_mph DECIMAL(10,2),
                    tip_pct DECIMAL(10,2),
                    
                    run_id VARCHAR(50),
                    source_year INTEGER,
                    source_month INTEGER,
                    ingested_at_utc TIMESTAMP
                );
            """)
            self.conn.commit()
        print("Tabla OBT creada")
    
    def build_obt_for_month(self, year, month, services, run_id):
        print(f"Procesando {year}-{month:02d}, servicios: {services}")
        
        with self.conn.cursor() as cursor:
            for service in services:
                if service == 'yellow':
                    pickup_col = 'tpep_pickup_datetime'
                    dropoff_col = 'tpep_dropoff_datetime'
                    table_name = 'yellow_taxi_trip'
                else:
                    pickup_col = 'lpep_pickup_datetime'
                    dropoff_col = 'lpep_dropoff_datetime'
                    table_name = 'green_taxi_trip'

                temp_table = f"analytics.obt_trips_{service}_{year}_{month:02d}"

                cursor.execute(f"DROP TABLE IF EXISTS {temp_table};")
                
                query = f"""
                CREATE TABLE {temp_table} AS
                SELECT 
                    {pickup_col} as pickup_datetime,
                    {dropoff_col} as dropoff_datetime,
                    EXTRACT(HOUR FROM {pickup_col}) as pickup_hour,
                    EXTRACT(DOW FROM {pickup_col}) as pickup_dow,
                    EXTRACT(MONTH FROM {pickup_col}) as month,
                    EXTRACT(YEAR FROM {pickup_col}) as year,
                    
                    pulocationid as pu_location_id,
                    COALESCE(puz."Zone", 'Unknown') as pu_zone,
                    COALESCE(puz."Borough", 'Unknown') as pu_borough,
                    dolocationid as do_location_id, 
                    COALESCE(doz."Zone", 'Unknown') as do_zone,
                    COALESCE(doz."Borough", 'Unknown') as do_borough,
                    
                    '{service}' as service_type,
                    vendorid as vendor_id,
                    CASE vendorid
                        WHEN 1 THEN 'Creative Mobile Technologies, LLC'
                        WHEN 2 THEN 'Curb Mobility, LLC'
                        WHEN 6 THEN 'Myle Technologies Inc'
                        WHEN 7 THEN 'Helix'
                        ELSE 'Unknown'
                    END as vendor_name,
                    ratecodeid as rate_code_id,
                    CASE ratecodeid
                        WHEN 1 THEN 'Standard rate'
                        WHEN 2 THEN 'JFK'
                        WHEN 3 THEN 'Newark'
                        WHEN 4 THEN 'Nassau or Westchester'
                        WHEN 5 THEN 'Negotiated fare'
                        WHEN 6 THEN 'Group ride'
                        ELSE 'Unknown'
                    END as rate_code_desc,
                    payment_type as payment_type,
                    CASE payment_type
                        WHEN 0 THEN 'Flex Fare trip'
                        WHEN 1 THEN 'Credit card'
                        WHEN 2 THEN 'Cash'
                        WHEN 3 THEN 'No charge'
                        WHEN 4 THEN 'Dispute'
                        WHEN 6 THEN 'Voided trip'
                        ELSE 'Unknown'
                    END as payment_type_desc,
                    passenger_count,
                    CASE WHEN trip_distance > 0 AND trip_distance < 100000 THEN trip_distance ELSE 0 END as trip_distance,
                    CASE WHEN fare_amount > 0 AND fare_amount < 100000 THEN fare_amount ELSE 0 END as fare_amount,
                    CASE WHEN extra > 0 AND extra < 100000 THEN extra ELSE 0 END as extra,
                    CASE WHEN mta_tax > 0 AND mta_tax < 100000 THEN mta_tax ELSE 0 END as mta_tax,
                    CASE WHEN tip_amount > 0 AND tip_amount < 100000 THEN tip_amount ELSE 0 END as tip_amount,
                    CASE WHEN tolls_amount > 0 AND tolls_amount < 100000 THEN tolls_amount ELSE 0 END as tolls_amount,
                    CASE WHEN improvement_surcharge > 0 AND improvement_surcharge < 100000 THEN improvement_surcharge ELSE 0 END as improvement_surcharge,
                    CASE WHEN congestion_surcharge > 0 AND congestion_surcharge < 100000 THEN congestion_surcharge ELSE 0 END as congestion_surcharge,
                    CASE WHEN airport_fee > 0 AND airport_fee < 100000 THEN airport_fee ELSE 0 END as airport_fee,
                    CASE WHEN total_amount > 0 AND total_amount < 100000 THEN total_amount ELSE 0 END as total_amount,
                    store_and_fwd_flag,
                    CASE 
                        WHEN EXTRACT(EPOCH FROM ({dropoff_col} - {pickup_col})) > 0
                            AND (EXTRACT(EPOCH FROM ({dropoff_col} - {pickup_col})) / 60) < 10000
                        THEN EXTRACT(EPOCH FROM ({dropoff_col} - {pickup_col})) / 60
                        ELSE 0
                    END AS trip_duration_min,
                    CASE 
                        WHEN EXTRACT(EPOCH FROM ({dropoff_col} - {pickup_col})) > 0
                             AND trip_distance / (EXTRACT(EPOCH FROM ({dropoff_col} - {pickup_col})) / 3600) < 150
                        THEN (trip_distance / (EXTRACT(EPOCH FROM ({dropoff_col} - {pickup_col})) / 3600))
                        ELSE 0 
                    END as avg_speed_mph,
                    CASE WHEN fare_amount > 0 AND (tip_amount / fare_amount * 100) < 10000 THEN (tip_amount / fare_amount * 100) ELSE 0 END as tip_pct,
                    
                    '{run_id}' as run_id,
                    source_year,
                    source_month,
                    ingested_at_utc
                    
                FROM raw.{table_name} t
                LEFT JOIN raw.taxi_zone_lookup puz ON t.pulocationid::text = puz."LocationID"
                LEFT JOIN raw.taxi_zone_lookup doz ON t.dolocationid::text = doz."LocationID"
                WHERE source_year = %s AND source_month = %s
                """
                
                cursor.execute(query, (year, month))
                print(f"{service}: tabla temporal creada para {year}-{month:02d}")

                merge_sql = f"""
                MERGE INTO analytics.obt_trips AS target
                USING {temp_table} AS source
                ON  target.vendor_id = source.vendor_id
                    AND target.pickup_datetime = source.pickup_datetime
                    AND target.dropoff_datetime = source.dropoff_datetime
                    AND target.pu_location_id = source.pu_location_id
                    AND target.do_location_id = source.do_location_id

                WHEN MATCHED THEN UPDATE SET
                    pickup_hour = source.pickup_hour,
                    pickup_dow = source.pickup_dow,
                    month = source.month,
                    year = source.year,
                    pu_zone = source.pu_zone,
                    pu_borough = source.pu_borough,
                    do_zone = source.do_zone,
                    do_borough = source.do_borough,
                    service_type = source.service_type,
                    vendor_name = source.vendor_name,
                    rate_code_id = source.rate_code_id,
                    rate_code_desc = source.rate_code_desc,
                    payment_type = source.payment_type,
                    payment_type_desc = source.payment_type_desc,
                    passenger_count = source.passenger_count,
                    trip_distance = source.trip_distance,
                    fare_amount = source.fare_amount,
                    extra = source.extra,
                    mta_tax = source.mta_tax,
                    tip_amount = source.tip_amount,
                    tolls_amount = source.tolls_amount,
                    improvement_surcharge = source.improvement_surcharge,
                    congestion_surcharge = source.congestion_surcharge,
                    airport_fee = source.airport_fee,
                    total_amount = source.total_amount,
                    store_and_fwd_flag = source.store_and_fwd_flag,
                    trip_duration_min = source.trip_duration_min,
                    avg_speed_mph = source.avg_speed_mph,
                    tip_pct = source.tip_pct,
                    run_id = source.run_id,
                    source_year = source.source_year,
                    source_month = source.source_month,
                    ingested_at_utc = source.ingested_at_utc

                WHEN NOT MATCHED THEN
                    INSERT (
                        pickup_datetime, dropoff_datetime, pickup_hour, pickup_dow, month, year,
                        pu_location_id, pu_zone, pu_borough, do_location_id, do_zone, do_borough,
                        service_type, vendor_id, vendor_name, rate_code_id, rate_code_desc,
                        payment_type, payment_type_desc,
                        passenger_count, trip_distance, fare_amount, extra, mta_tax, tip_amount,
                        tolls_amount, improvement_surcharge, congestion_surcharge, airport_fee,
                        total_amount, store_and_fwd_flag,
                        trip_duration_min, avg_speed_mph, tip_pct,
                        run_id, source_year, source_month, ingested_at_utc
                    )
                    VALUES (
                        source.pickup_datetime, source.dropoff_datetime, source.pickup_hour, source.pickup_dow, source.month, source.year,
                        source.pu_location_id, source.pu_zone, source.pu_borough, source.do_location_id, source.do_zone, source.do_borough,
                        source.service_type, source.vendor_id, source.vendor_name, source.rate_code_id, source.rate_code_desc,
                        source.payment_type, source.payment_type_desc,
                        source.passenger_count, source.trip_distance, source.fare_amount, source.extra, source.mta_tax, source.tip_amount,
                        source.tolls_amount, source.improvement_surcharge, source.congestion_surcharge, source.airport_fee,
                        source.total_amount, source.store_and_fwd_flag,
                        source.trip_duration_min, source.avg_speed_mph, source.tip_pct,
                        source.run_id, source.source_year, source.source_month, source.ingested_at_utc
                    );
                    """
                cursor.execute(merge_sql)
                print(f"  {service}: MERGE ejecutado correctamente.")


                cursor.execute(f"DROP TABLE IF EXISTS {temp_table};")
                print(f"  {service}: tabla temporal eliminada.")
            
            self.conn.commit()
    
    def build_obt(self, year_start, year_end, services, run_id, months=None):
        print(f"Construyendo OBT para {year_start}-{year_end}, servicios: {services}")
        
        if months is None:
            months = list(range(1, 13))
        
        for year in range(year_start, year_end + 1):
            for month in months:
                self.build_obt_for_month(year, month, services, run_id)  
                print(f"Procesado {year}-{month:02d}")

    def run(self, year_start, year_end, services, run_id, months=None):
        try:
            self.connect()
            self.create_obt_table()
            self.build_obt(year_start, year_end, services, run_id, months)
        except Exception as e:
            print(f"Error: {e}")
            raise
        finally:
            self.disconnect()


def main():
    parser = argparse.ArgumentParser(description='Constructor OBT NYC Taxi')
    parser.add_argument('--year-start', type=int, required=True, help='Año inicial')
    parser.add_argument('--year-end', type=int, required=True, help='Año final')
    parser.add_argument('--services', type=str, default='yellow,green', help='Servicios')
    parser.add_argument('--run-id', type=str, required=True, help='ID de ejecución')
    parser.add_argument('--months', type=int, nargs='+', help='Meses específicos a procesar')
    
    args = parser.parse_args()
    
    db_params = {
        'host': os.getenv('PG_HOST'),
        'port': os.getenv('PG_PORT'),
        'database': os.getenv('PG_DB'),
        'user': os.getenv('PG_USER'),
        'password': os.getenv('PG_PASSWORD')
    }
    
    services = args.services.split(',')
    
    builder = OBTBuilder(db_params)
    builder.run(args.year_start, args.year_end, services, args.run_id, args.months)


if __name__ == '__main__':
    main()