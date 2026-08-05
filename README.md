# Data Engineering Zoomcamp Portfolio

Hands-on data engineering projects built while completing the [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp). This repository demonstrates the end-to-end skills involved in moving data from ingestion to cloud storage, orchestration, validation, and analytics-ready transformation.

## Highlights

- Built a containerized Python ingestion application that loads NYC Taxi data into PostgreSQL in chunks.
- Developed an Apache Airflow DAG that extracts paginated data, writes partitioned Parquet data to Amazon S3 with `dlt`, and validates it with DuckDB.
- Provisioned cloud data-lake infrastructure with Terraform, including private S3 access and server-side encryption.
- Created a dbt project with layered staging and mart models, source freshness checks, schema tests, and a custom data-quality test.

## Projects

| Project | What it demonstrates | Main technologies |
| --- | --- | --- |
| [Docker & PostgreSQL ingestion](./pipeline/README.md) | Downloading and chunk-loading NYC Yellow Taxi and zone lookup data into Postgres | Python, Pandas, SQLAlchemy, PostgreSQL, Docker, pgAdmin |
| [Orchestrated NYC Taxi pipeline](./airflow/README.md) | Extracting API data, loading Parquet to S3, validating and querying it, all orchestrated by Airflow | Airflow, dlt, AWS S3, DuckDB, Terraform, Docker, Python |
| [dbt Jaffle Shop analytics](./dbt/jaffle_shop/README.md) | Transforming raw retail data into documented, tested staging and mart models | dbt, SQL, data quality testing |
| [AWS foundations](./terraform) | Creating an S3 bucket and AWS Glue Catalog database | Terraform, AWS S3, AWS Glue |

## Featured pipeline: NYC Taxi API to S3

The Airflow project is the repository's most complete end-to-end implementation. It processes NYC Taxi data from the Zoomcamp workshop API and produces analytics-ready Parquet files in an S3 data lake.

```text
NYC Taxi API
    |
    v
Python extractor (paginated requests)
    |
    v
dlt normalization + Parquet files
    |
    v
Amazon S3 data lake  <--- Terraform provisioning
    |
    v
DuckDB validation and SQL analysis

Apache Airflow orchestrates each stage
```

The DAG runs the following sequence:

1. Extracts every available API page and loads the data to S3 as Parquet using `dlt`.
2. Validates that the Parquet dataset is non-empty and inspects its schema directly from S3 with DuckDB.
3. Runs SQL analysis for trip dates, payment-type distribution, credit-card share, and total tips.

The load uses replacement semantics, so a successful rerun refreshes the dataset rather than duplicating it.

## Repository layout

```text
.
|-- airflow/                 # Airflow DAG, extraction/validation scripts, and S3 Terraform
|-- dbt/jaffle_shop/         # dbt staging and mart models for Jaffle Shop
|-- pipeline/                # Dockerized NYC Taxi to PostgreSQL ingestion application
`-- terraform/               # Introductory AWS S3 and Glue Terraform configuration
```

## Skills demonstrated

- **Data ingestion:** API pagination, CSV ingestion, chunked loading, schema-aware parsing
- **Data storage:** PostgreSQL, Amazon S3, Parquet
- **Orchestration:** Apache Airflow DAGs, task dependencies, retries, CeleryExecutor
- **Transformation:** dbt staging and mart layers, reusable SQL models
- **Data quality:** dbt source/model tests, freshness checks, custom assertions, DuckDB validation
- **Infrastructure as code:** Terraform-managed AWS resources and secure S3 defaults
- **Developer tooling:** Docker Compose, environment-based configuration, Python packaging

## Running the projects

Each project is independently runnable and has its own setup instructions:

- For the local Docker/PostgreSQL ingestion project, see [pipeline/README.md](./pipeline/README.md).
- For the Airflow, S3, and Terraform pipeline, see [airflow/README.md](./airflow/README.md).
- For the dbt project, create a matching `jaffle_shop` profile in your local `profiles.yml`, then run `dbt deps`, `dbt run`, and `dbt test` from `dbt/jaffle_shop`.

### Requirements

Depending on the project you want to run, install:

- Docker Desktop and Docker Compose
- Python 3.13+ for the local ingestion project
- Terraform and AWS CLI for the AWS-backed pipeline
- dbt plus an accessible warehouse/database for the dbt project

## Security and cost note

AWS credentials, Terraform state, local environment files, and generated artifacts are excluded from version control. The AWS projects can create billable resources; review the Terraform plan before applying it and destroy resources when finished.

## About

This repository is a learning portfolio. It is intended to show practical data engineering work: clear project structure, reproducible local environments, cloud infrastructure, orchestration, and quality-focused transformations.

Explore the individual projects above for implementation details and setup instructions.
