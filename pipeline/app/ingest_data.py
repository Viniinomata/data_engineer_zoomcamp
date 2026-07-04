#!/usr/bin/env python
# coding: utf-8

import os

import click
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from tqdm import tqdm

YELLOW_TAXI_URL = (
    "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/"
    "yellow_tripdata_2021-01.csv.gz"
)

YELLOW_TAXI_DTYPE = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64",
}

YELLOW_TAXI_PARSE_DATES = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
]


ZONE_LOOKUP_DTYPE = {
    "LocationID": "Int64",
    "Borough": "string",
    "Zone": "string",
    "service_zone": "string",
}


def build_database_url(pg_user, pg_pass, pg_host, pg_port, pg_db):
    return (
        f"postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
    )


def resolve_dataset_config(data_url, target_table):
    source_name = os.path.basename(data_url).lower()
    table_name = target_table.lower()

    if "taxi_zone" in source_name or table_name == "zones":
        return {
            "dtype": ZONE_LOOKUP_DTYPE,
            "parse_dates": None,
        }

    if "yellow_tripdata" in source_name or table_name == "yellow_taxi_data":
        return {
            "dtype": YELLOW_TAXI_DTYPE,
            "parse_dates": YELLOW_TAXI_PARSE_DATES,
        }

    return {
        "dtype": None,
        "parse_dates": None,
    }


def ingest_data(data_url, target_table, engine, chunksize):
    dataset_config = resolve_dataset_config(
        data_url=data_url,
        target_table=target_table,
    )
    read_csv_kwargs = {
        "filepath_or_buffer": data_url,
        "iterator": True,
        "chunksize": chunksize,
    }

    if dataset_config["dtype"] is not None:
        read_csv_kwargs["dtype"] = dataset_config["dtype"]

    if dataset_config["parse_dates"] is not None:
        read_csv_kwargs["parse_dates"] = dataset_config["parse_dates"]

    df_iter = pd.read_csv(**read_csv_kwargs)

    for i, df_chunk in enumerate(tqdm(df_iter, desc="Processing chunks")):
        if i == 0:
            df_chunk.head(0).to_sql(
                name=target_table,
                con=engine,
                if_exists="replace",
                index=False,
            )
            print(f"Table '{target_table}' created")

        df_chunk.to_sql(
            name=target_table,
            con=engine,
            if_exists="append",
            index=False,
        )

        print(f"Inserted chunk #{i}: {len(df_chunk)} rows")


@click.command()
@click.option("--pg-user", default="root", help="PostgreSQL user")
@click.option("--pg-pass", default="root", help="PostgreSQL password")
@click.option("--pg-host", default="localhost", help="PostgreSQL host")
@click.option("--pg-port", default=5432, type=int, help="PostgreSQL port")
@click.option("--pg-db", default="ny_taxi", help="PostgreSQL database name")
@click.option(
    "--target-table", default="yellow_taxi_data", help="Target table name"
)
@click.option(
    "--data-url", default=YELLOW_TAXI_URL, help="CSV/CSV.GZ file URL or path"
)
@click.option("--chunksize", default=100_000, type=int, help="Rows per chunk")
@click.option(
    "--use-env",
    is_flag=True,
    help="Use DATABASE_URL from .env instead of command-line database arguments",
)
def run(
    pg_user,
    pg_pass,
    pg_host,
    pg_port,
    pg_db,
    target_table,
    data_url,
    chunksize,
    use_env,
):
    load_dotenv()

    if use_env:
        database_url = os.environ.get("DATABASE_URL")

        if database_url is None:
            raise ValueError(
                "DATABASE_URL was not found. Check your .env file or run without --use-env."
            )
    else:
        database_url = build_database_url(
            pg_user=pg_user,
            pg_pass=pg_pass,
            pg_host=pg_host,
            pg_port=pg_port,
            pg_db=pg_db,
        )

    engine = create_engine(database_url)

    ingest_data(
        data_url=data_url,
        target_table=target_table,
        engine=engine,
        chunksize=chunksize,
    )


if __name__ == "__main__":
    run()
