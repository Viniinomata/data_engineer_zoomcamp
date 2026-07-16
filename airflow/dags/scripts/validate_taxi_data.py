import os

import duckdb


def validate_taxi_data() -> None:
    bucket = os.environ["AWS_S3_BUCKET"]
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

    parquet_path = f"s3://{bucket}/nyc_taxi/taxi_trips/*.parquet"

    connection = duckdb.connect()

    connection.execute("INSTALL httpfs")
    connection.execute("LOAD httpfs")

    connection.execute(f"""
        CREATE OR REPLACE SECRET aws_secret (
            TYPE s3,
            PROVIDER credential_chain,
            REGION '{region}'
        )
        """)

    row_count = connection.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{parquet_path}')
        """).fetchone()[0]

    columns = connection.execute(f"""
        DESCRIBE
        SELECT *
        FROM read_parquet('{parquet_path}')
        """).fetchall()

    print(f"Parquet location: {parquet_path}")
    print(f"Total rows: {row_count}")
    print("Columns:")

    for column in columns:
        print(f"  {column[0]}: {column[1]}")

    if row_count == 0:
        raise ValueError("Validation failed: the dataset contains no rows.")

    connection.close()


if __name__ == "__main__":
    validate_taxi_data()
