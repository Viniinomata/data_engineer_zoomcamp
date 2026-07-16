import os
from pathlib import Path

import duckdb


def load_sql_queries(file_name: str) -> dict[str, str]:
    sql_path = Path(__file__).resolve().parent.parent / "sql" / file_name
    sql_content = sql_path.read_text(encoding="utf-8")

    queries: dict[str, str] = {}
    current_name: str | None = None
    current_lines: list[str] = []

    for line in sql_content.splitlines():
        if line.startswith("-- name:"):
            if current_name and current_lines:
                queries[current_name] = "\n".join(current_lines).strip()
            current_name = line.split(":", 1)[1].strip()
            current_lines = []
            continue

        if current_name:
            current_lines.append(line)

    if current_name and current_lines:
        queries[current_name] = "\n".join(current_lines).strip()

    if not queries:
        raise ValueError(f"No named SQL queries found in {sql_path}")

    return queries

def answer_workshop_questions() -> None:
    bucket = os.environ["AWS_S3_BUCKET"]
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    queries = load_sql_queries("workshop_questions.sql")

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

    connection.execute(f"""
        CREATE OR REPLACE VIEW taxi_trips AS
        SELECT *
        FROM read_parquet('{parquet_path}')
        """)

    columns = connection.execute("DESCRIBE taxi_trips").fetchall()

    print("Available columns:")
    for column in columns:
        print(f"  {column[0]}: {column[1]}")

    date_range = connection.execute(queries["date_range"]).fetchone()
    payment_types = connection.execute(queries["payment_types"]).fetchall()
    credit_card_percentage = connection.execute(
        queries["credit_card_percentage"]
    ).fetchone()[0]
    total_tips = connection.execute(queries["total_tips"]).fetchone()[0]

    print()
    print(f"Earliest trip: {date_range[0]}")
    print(f"Latest trip: {date_range[1]}")

    print("\nPayment types:")
    for payment_type, trips in payment_types:
        print(f"  {payment_type}: {trips}")

    print(f"\nCredit-card percentage: {credit_card_percentage:.2f}%")
    print(f"Total tips: ${total_tips:,.2f}")

    connection.close()


if __name__ == "__main__":
    answer_workshop_questions()
