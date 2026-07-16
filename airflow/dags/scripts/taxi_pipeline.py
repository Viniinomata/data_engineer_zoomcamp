import os
from collections.abc import Iterator
from typing import Any

import dlt
import requests

API_URL = (
    "https://us-central1-dlthub-analytics.cloudfunctions.net/"
    "data_engineering_zoomcamp_api"
)


@dlt.resource(
    name="taxi_trips",
    write_disposition="replace",
)
def taxi_trips() -> Iterator[list[dict[str, Any]]]:
    """Extract all taxi-trip pages from the Zoomcamp API."""

    page = 1

    while True:
        response = requests.get(
            API_URL,
            params={"page": page},
            timeout=60,
        )
        response.raise_for_status()

        records = response.json()

        if not isinstance(records, list):
            raise TypeError(
                f"Expected a JSON list, received {type(records).__name__}"
            )

        if not records:
            print(f"Pagination finished at empty page {page}.")
            break

        print(f"Extracted page {page}: {len(records)} records")
        yield records

        page += 1


def run_pipeline() -> None:
    bucket_name = os.environ["AWS_S3_BUCKET"]
    bucket_url = f"s3://{bucket_name}"

    destination = dlt.destinations.filesystem(
        bucket_url=bucket_url,
    )

    pipeline = dlt.pipeline(
        pipeline_name="zoomcamp_taxi_pipeline",
        destination=destination,
        dataset_name="nyc_taxi",
    )

    load_info = pipeline.run(
        taxi_trips(),
        loader_file_format="parquet",
    )

    print(load_info)


if __name__ == "__main__":
    run_pipeline()
