# Docker Workshop

This project is based on the data engineer Zoomcamp. It provisions PostgreSQL and pgAdmin with Docker Compose, then loads NYC yellow taxi trip data and taxi zone lookup data into Postgres through a separate ingestion image.

## Project Structure

```text
pipeline/
  app/
    ingest_data.py
  data/
    taxi_zone_lookup.csv
  Dockerfile
  docker-compose.yaml
  pyproject.toml
  uv.lock
  README.md
```

## Prerequisites

- Docker Desktop installed and running
- PowerShell

## Environment File

This project supports loading `DATABASE_URL` from a local `.env` file.

Use `pipeline/.env.example` as a template and create your own `pipeline/.env` with the real connection string you use locally.

## 1. Start PostgreSQL, pgAdmin, and the Docker Network

From the `pipeline` directory:

```powershell
docker compose up -d
```

This starts:

- PostgreSQL
- pgAdmin
- a Docker bridge network named `pg-network`

Check the running containers:

```powershell
docker ps
```

## 2. Build the Ingestion Image

Still in the `pipeline` directory:

```powershell
docker build -t taxi_ingest:v001 .
```

Rebuild the image whenever you change `app/ingest_data.py` or `Dockerfile`.

## 3. Load Yellow Taxi Data

Run the ingestion container on the same network as PostgreSQL:

```powershell
docker run -it `
  --network=pipeline_pg-network `
  taxi_ingest:v001 `
  --pg-user=root `
  --pg-pass=root `
  --pg-host=pgdatabase `
  --pg-port=5432 `
  --pg-db=ny_taxi `
  --target-table=yellow_taxi_trips
```

This creates and loads the `yellow_taxi_trips` table.

## 4. Load Taxi Zones Data

The zone lookup CSV is already copied into the image under `data/`, so load it like this:

```powershell
docker run -it `
  --network=pipeline_pg-network `
  taxi_ingest:v002 `
  --pg-user=root `
  --pg-pass=root `
  --pg-host=pgdatabase `
  --pg-port=5432 `
  --pg-db=ny_taxi `
  --target-table=zones `
  --data-url data/taxi_zone_lookup.csv `
  --chunksize 100
```

This creates and loads the `zones` table.

## 5. Open pgAdmin

Open:

```text
http://localhost:8085
```

Login with:

- Email: `admin@admin.com`
- Password: `root`

Register the PostgreSQL server with:

- Host name/address: `pgdatabase`
- Port: `5432`
- Maintenance database: `ny_taxi`
- Username: `root`
- Password: `root`

## 6. Query the Data

Check the trips table:

```sql
SELECT *
FROM yellow_taxi_trips
LIMIT 10;
```

Join trips with pickup and dropoff zones:

```sql
SELECT
    t."VendorID",
    t."tpep_pickup_datetime",
    t."tpep_dropoff_datetime",
    zpu."Zone" AS pickup_zone,
    zdo."Zone" AS dropoff_zone
FROM yellow_taxi_trips t
JOIN zones zpu ON t."PULocationID" = zpu."LocationID"
JOIN zones zdo ON t."DOLocationID" = zdo."LocationID"
LIMIT 100;
```

## Useful Commands

Stop the stack:

```powershell
docker compose down
```

Stop the stack and remove volumes:

```powershell
docker compose down -v
```

List networks:

```powershell
docker network ls
```

List containers:

```powershell
docker ps
```
