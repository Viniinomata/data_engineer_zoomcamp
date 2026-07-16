# NYC Taxi Data Pipeline — Airflow, dlt, AWS S3, DuckDB, and Terraform

This project is an AWS adaptation of the 2026 Data Engineering Zoomcamp `dlt` workshop.

It extracts paginated NYC taxi data from the workshop API, normalizes and loads the records as Parquet files into Amazon S3, validates the resulting dataset with DuckDB, and answers the workshop questions. Apache Airflow orchestrates the workflow, while Terraform provisions the S3 infrastructure.

## Architecture

```text
Zoomcamp NYC Taxi API
        |
        v
Python + requests
        |
        v
dlt normalization and Parquet loading
        |
        v
Amazon S3
        |
        v
DuckDB validation and SQL analysis

Apache Airflow orchestrates the complete workflow.
Terraform provisions the AWS S3 bucket.
```

The Airflow DAG runs these tasks in order:

```text
ingest_taxi_data
        |
        v
validate_parquet_data
        |
        v
answer_workshop_questions_task
```

## What the project does

1. Calls the Zoomcamp API one page at a time.
2. Stops pagination when the API returns an empty list.
3. Uses `dlt` to infer the schema, normalize records, create Parquet files, and upload them to S3.
4. Uses `write_disposition="replace"` so rerunning the pipeline replaces the previous taxi table instead of duplicating it.
5. Uses DuckDB to read the Parquet files directly from S3.
6. Validates that the dataset contains rows and prints its schema.
7. Runs SQL queries that calculate:
   - the earliest and latest trip dates;
   - the distribution of payment types;
   - the percentage of trips paid by credit card;
   - the total tip amount.

## Technology stack

- Apache Airflow 3.3.0
- Docker and Docker Compose
- Python
- `dlt`
- Amazon S3
- Terraform
- DuckDB
- PostgreSQL and Redis for the local Airflow deployment
- CeleryExecutor

## Project structure

```text
airflow/
├── config/
│   └── airflow.cfg
├── dags/
│   ├── scripts/
│   │   ├── answer_workshop_questions.py
│   │   ├── taxi_extractor.py
│   │   ├── taxi_pipeline.py
│   │   └── validate_taxi_data.py
│   ├── sql/
│   │   └── workshop_questions.sql
│   └── taxi_pipeline_dag.py
├── terraform/
│   ├── .terraform.lock.hcl
│   ├── main.tf
│   ├── outputs.tf
│   ├── terraform.tfvars
│   └── variables.tf
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
├── .env
└── README.md
```

## Prerequisites

Install these tools before starting:

- Docker Desktop with Linux containers enabled
- Docker Compose v2
- Terraform 1.7 or newer
- AWS CLI v2
- An AWS account
- Git, if the project will be version-controlled

Confirm the installations:

```powershell
docker version
docker compose version
terraform version
aws --version
```

Docker must show both a `Client` and a `Server` section.

## 1. Configure AWS credentials

Configure an AWS CLI profile on the host machine:

```powershell
aws configure
```

Provide:

```text
AWS Access Key ID:     your access key
AWS Secret Access Key: your secret key
Default region name:   us-east-1
Default output format: json
```

Verify the authenticated identity:

```powershell
aws sts get-caller-identity
```

The AWS identity needs permission to create and manage the workshop S3 bucket and to read and write objects in it.

Never commit AWS credentials to Git.

## 2. Configure Terraform variables

Open:

```text
terraform/terraform.tfvars
```

Use values similar to:

```hcl
aws_region   = "us-east-1"
project_name = "zoomcamp-airflow"
bucket_name  = "replace-with-a-globally-unique-bucket-name"
```

S3 bucket names are globally unique across AWS, so choose a name that no other AWS account is using.

The Terraform configuration creates:

- a private S3 bucket;
- an S3 Block Public Access configuration;
- explicit SSE-S3 encryption using AES-256.

It does not create Athena or Glue resources.

## 3. Provision AWS resources with Terraform

From the project root:

```powershell
cd .\terraform
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply
```

Review the plan before typing:

```text
yes
```

Display the resulting bucket name:

```powershell
terraform output
terraform output -raw bucket_name
```

Return to the project root:

```powershell
cd ..
```

Verify that the bucket exists:

```powershell
aws s3 ls
```

## 4. Create the Airflow environment file

Create or update `.env` in the same directory as `docker-compose.yaml`:

```env
AIRFLOW_UID=50000
FERNET_KEY=replace-with-a-valid-fernet-key
AWS_ACCESS_KEY_ID=replace-with-your-access-key-id
AWS_SECRET_ACCESS_KEY=replace-with-your-secret-access-key
AWS_DEFAULT_REGION=us-east-1
AWS_S3_BUCKET=replace-with-the-terraform-bucket-name
```

The Compose configuration passes these AWS values to all Airflow services.

To generate a Fernet key with the Airflow image:

```powershell
docker run --rm apache/airflow:3.3.0 `
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Do not add quotes around values in `.env` unless the value itself requires them.

## 5. Protect secrets and generated files

Create a `.gitignore` containing at least:

```gitignore
.env
.aws/
__pycache__/
*.pyc
logs/

terraform/.terraform/
terraform/*.tfstate
terraform/*.tfstate.*
terraform/terraform.tfvars
```

A Terraform state file may contain infrastructure details and, depending on the resources used, sensitive values. Do not publish it.

Create a safe example file for other users:

```text
terraform/terraform.tfvars.example
```

Example:

```hcl
aws_region   = "us-east-1"
project_name = "zoomcamp-airflow"
bucket_name  = "replace-with-a-globally-unique-bucket-name"
```

## 6. Build the custom Airflow image

The `Dockerfile` extends the official Airflow image and installs the dependencies from `requirements.txt`:

```text
dlt[filesystem]
s3fs
boto3
requests
duckdb
```

Build the image:

```powershell
docker compose build
```

Use `--no-cache` when dependencies changed and Docker keeps reusing an old layer:

```powershell
docker compose build --no-cache
```

## 7. Initialize Airflow

Run the one-time initialization service:

```powershell
docker compose up airflow-init
```

Wait for it to finish successfully.

The initialization performs the database migration, creates the initial Airflow account, and prepares the mounted directories.

## 8. Start Airflow

Start all services in the background:

```powershell
docker compose up -d
```

Check their status:

```powershell
docker compose ps
```

The main services include:

- `airflow-apiserver`
- `airflow-scheduler`
- `airflow-dag-processor`
- `airflow-worker`
- `airflow-triggerer`
- `postgres`
- `redis`

Open the Airflow UI:

```text
http://localhost:8080
```

Unless changed in `.env`, the local development credentials are commonly:

```text
Username: airflow
Password: airflow
```

## 9. Verify the Python dependencies

Run:

```powershell
docker compose exec airflow-scheduler `
  python -c "import dlt, boto3, requests, s3fs, duckdb; print('Dependencies installed'); print('dlt:', dlt.__version__); print('DuckDB:', duckdb.__version__)"
```

## 10. Verify AWS access from Airflow

Check the AWS identity available inside the container:

```powershell
docker compose exec airflow-scheduler `
  python -c "import boto3; print(boto3.client('sts').get_caller_identity())"
```

Check access to the configured bucket:

```powershell
docker compose exec airflow-scheduler `
  python -c "import boto3, os; bucket=os.environ['AWS_S3_BUCKET']; boto3.client('s3').head_bucket(Bucket=bucket); print('S3 access successful:', bucket)"
```

## 11. Optional: test the API extractor manually

The extraction-only script tests pagination without writing data to S3:

```powershell
docker compose exec airflow-worker `
  python /opt/airflow/dags/scripts/taxi_extractor.py
```

It should print each page and finish with the total number of pages and records.

The source API is:

```text
https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api
```

Each request uses a `page` query parameter. Pagination stops when the API returns an empty JSON list.

## 12. Optional: run each stage manually

Manual execution is useful for debugging before using the DAG.

### Ingestion

```powershell
docker compose exec airflow-worker `
  python /opt/airflow/dags/scripts/taxi_pipeline.py
```

### Validation

```powershell
docker compose exec airflow-worker `
  python /opt/airflow/dags/scripts/validate_taxi_data.py
```

### Workshop questions

```powershell
docker compose exec airflow-worker `
  python /opt/airflow/dags/scripts/answer_workshop_questions.py
```

`airflow-worker` is used here because the project uses `CeleryExecutor`, and the worker is the service that normally executes Airflow task code. Other Airflow containers share the same image and mounts, but the worker most closely represents actual DAG execution.

## 13. Check that Airflow parsed the DAG

List DAGs:

```powershell
docker compose exec airflow-scheduler airflow dags list
```

Check import errors:

```powershell
docker compose exec airflow-scheduler airflow dags list-import-errors
```

The DAG ID is:

```text
zoomcamp_taxi_pipeline
```

## 14. Run the pipeline through Airflow

1. Open `http://localhost:8080`.
2. Find `zoomcamp_taxi_pipeline`.
3. Unpause the DAG if needed.
4. Open it.
5. Click **Trigger DAG**.
6. Watch the tasks run in this order:

```text
ingest_taxi_data
        |
        v
validate_parquet_data
        |
        v
answer_workshop_questions_task
```

The DAG is configured with:

- no automatic schedule (`schedule=None`);
- no backfill (`catchup=False`);
- a maximum of one active DAG run;
- two retries per task;
- a two-minute retry delay.

## 15. Where the S3 data is stored

The pipeline configures the filesystem destination at the bucket root and uses the dlt dataset name `nyc_taxi` and resource name `taxi_trips`.

The business data is therefore stored under:

```text
s3://YOUR_BUCKET/nyc_taxi/taxi_trips/
```

The Parquet files are inside that prefix:

```text
s3://YOUR_BUCKET/nyc_taxi/taxi_trips/*.parquet
```

List them with:

```powershell
aws s3 ls s3://YOUR_BUCKET/nyc_taxi/taxi_trips/ --recursive
```

The `nyc_taxi` dataset also contains dlt metadata, such as:

```text
_dlt_loads/
_dlt_pipeline_state/
_dlt_version/
init
```

These directories are expected. They store pipeline load information, state, and schema/version metadata. The actual taxi records are in `taxi_trips/`.

## 16. Data replacement behavior

The dlt resource uses:

```python
write_disposition="replace"
```

This means a successful rerun replaces the existing `taxi_trips` table files rather than appending another full copy of the source dataset.

Run the DAG twice and compare the validation row count. It should remain stable rather than double.

## 17. Validation behavior

`validate_taxi_data.py`:

- loads DuckDB's `httpfs` extension;
- authenticates through the AWS credential chain;
- reads all matching Parquet files directly from S3;
- prints the row count;
- prints the inferred columns and types;
- raises an exception if the dataset contains zero rows.

Because an exception causes the Airflow task to fail, the analysis task will not run after a failed validation.

## 18. SQL analysis

The SQL queries are stored in:

```text
dags/sql/workshop_questions.sql
```

The Python analysis script loads named queries from that file and executes them against a DuckDB view called `taxi_trips`.

The queries calculate:

- minimum and maximum `trip_pickup_date_time`;
- trip counts by `payment_type`;
- the percentage where `payment_type` is `credit card`;
- the sum of `tip_amt`.

The results appear in the logs of:

```text
answer_workshop_questions_task
```

## 19. View logs

Follow all Compose logs:

```powershell
docker compose logs -f
```

Follow only the worker logs:

```powershell
docker compose logs -f airflow-worker
```

Task-specific logs are also available in the Airflow UI.

## 20. Stop and restart the environment

Stop containers while keeping volumes:

```powershell
docker compose down
```

Start them again:

```powershell
docker compose up -d
```

Remove containers and the local PostgreSQL volume:

```powershell
docker compose down -v
```

Using `-v` deletes the local Airflow metadata database, including users, DAG-run history, and task history.

## 21. Destroy the AWS infrastructure

The S3 bucket must be empty before Terraform can delete it with the current configuration.

First, remove the objects:

```powershell
$bucket = terraform -chdir=terraform output -raw bucket_name
aws s3 rm "s3://$bucket" --recursive
```

Then destroy the Terraform-managed resources:

```powershell
terraform -chdir=terraform destroy
```

Review the plan and type:

```text
yes
```

## Troubleshooting

### Docker shows a client but no server

Start Docker Desktop and wait for the Linux engine to be ready:

```powershell
docker version
```

A working installation shows both `Client` and `Server`.

### Airflow cannot import a package

Rebuild the custom image:

```powershell
docker compose down
docker compose build --no-cache
docker compose up airflow-init
docker compose up -d
```

### The DAG does not appear

Check parsing errors:

```powershell
docker compose exec airflow-scheduler airflow dags list-import-errors
```

Also confirm that `dags/taxi_pipeline_dag.py` is mounted at:

```text
/opt/airflow/dags/taxi_pipeline_dag.py
```

### AWS returns `AccessDenied`

Confirm the active identity:

```powershell
aws sts get-caller-identity
```

Then confirm that the same credentials are present in `.env` and that the IAM identity can access the configured bucket.

After changing `.env`, recreate the containers:

```powershell
docker compose down
docker compose up -d
```

### DuckDB cannot find Parquet files

Confirm the exact S3 prefix:

```powershell
aws s3 ls s3://YOUR_BUCKET/nyc_taxi/taxi_trips/ --recursive
```

The current scripts expect:

```text
s3://YOUR_BUCKET/nyc_taxi/taxi_trips/*.parquet
```

### Terraform cannot delete the bucket

Empty it first:

```powershell
aws s3 rm s3://YOUR_BUCKET --recursive
terraform -chdir=terraform destroy
```

## Security notes

This Docker Compose configuration is intended for local development and learning, not production.

For a production deployment:

- do not place long-lived access keys in `.env`;
- prefer IAM roles or temporary credentials;
- use least-privilege IAM policies;
- store secrets in a dedicated secret manager;
- use a remote, encrypted Terraform backend with state locking;
- pin Python dependency versions;
- add monitoring and alerting;
- configure backup and recovery policies;
- use a managed Airflow deployment or a properly secured cluster.

## Project status

The project is complete when:

- Terraform creates the S3 bucket successfully;
- Airflow can authenticate to AWS;
- the DAG imports without errors;
- all three tasks finish successfully;
- Parquet files exist in S3;
- validation reports a nonzero row count;
- the workshop answers appear in the final task logs;
- rerunning the DAG does not duplicate the full dataset.
