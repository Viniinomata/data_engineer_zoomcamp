from collections.abc import Iterator
from typing import Any

import requests

API_URL = (
    "https://us-central1-dlthub-analytics.cloudfunctions.net/"
    "data_engineering_zoomcamp_api"
)


def extract_taxi_pages() -> Iterator[list[dict[str, Any]]]:
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
            print(f"Pagination finished. Page {page} was empty.")
            break

        print(f"Page {page}: {len(records)} records")
        yield records

        page += 1


if __name__ == "__main__":
    total_records = 0
    total_pages = 0

    for records in extract_taxi_pages():
        total_pages += 1
        total_records += len(records)

    print(f"Pages extracted: {total_pages}")
    print(f"Total records extracted: {total_records}")