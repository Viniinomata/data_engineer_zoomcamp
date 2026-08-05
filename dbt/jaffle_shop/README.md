# Jaffle Shop dbt Project

A dbt analytics project that turns raw Jaffle Shop customer, order, and Stripe payment data into tested, analytics-ready models. It demonstrates a practical dbt workflow: source definitions, staging models, business-facing marts, documentation, freshness monitoring, and automated data-quality tests.

## What this project delivers

- Standardized staging views for customers, orders, and Stripe payments.
- An `fct_orders` fact table containing successful order payments.
- A `dim_customers` mart that brings together customer attributes, order activity, and payment value.
- Source and model tests that check required fields, key uniqueness, allowed values, and referential integrity.
- Source freshness checks for the raw Jaffle Shop and Stripe datasets.
- A custom test that flags orders with negative total payment amounts.

## Data lineage

```text
raw.jaffle_shop.customers --> stg_jaffle_shop__customers --+
raw.jaffle_shop.orders -----> stg_jaffle_shop__orders -----+--> fct_orders --> dim_customers
raw.stripe.payment ---------> stg_stripe__payments --------+
```

## Model layers

| Layer | Models | Materialization | Purpose |
| --- | --- | --- | --- |
| Sources | `jaffle_shop.customers`, `jaffle_shop.orders`, `stripe.payment` | External raw tables | Declared and documented raw inputs |
| Staging | `stg_jaffle_shop__customers`, `stg_jaffle_shop__orders`, `stg_stripe__payments` | Views | Rename fields, apply consistent keys, and normalize payment amounts |
| Marts | `fct_orders`, `dim_customers` | Tables | Provide reusable, business-ready order and customer datasets |

## Data quality

The project includes dbt tests for:

- unique and non-null customer and order identifiers;
- non-null source fields;
- permitted order, payment-method, and payment-status values;
- order-to-customer relationships;
- source freshness, with warnings after 6 hours and errors after 12 hours;
- non-negative total payments through the custom test in [`tests/assert_positive_total_for_payments.sql`](./tests/assert_positive_total_for_payments.sql).

The `order_status` field is also documented in [`models/staging/jaffle_shop_docs.md`](./models/staging/jaffle_shop_docs.md).

## Prerequisites

- dbt Core and the adapter for your target warehouse
- Access to a warehouse containing these source tables:
  - `raw.jaffle_shop.customers`
  - `raw.jaffle_shop.orders`
  - `raw.stripe.payment`
- A local dbt profile named `jaffle_shop`

This repository does not include `profiles.yml` or warehouse credentials. Keep them in your local dbt configuration directory (`~/.dbt/profiles.yml`) or supply a custom profiles directory with `--profiles-dir`.

## Setup and run

From this directory:

```bash
dbt debug
dbt deps
dbt source freshness
dbt build
```

`dbt build` runs the models and their tests in dependency order. To run the individual steps instead:

```bash
dbt run
dbt test
```

Generate and serve the documentation site locally:

```bash
dbt docs generate
dbt docs serve
```

## Project structure

```text
.
|-- models/
|   |-- staging/       # Source definitions, staging views, and field documentation
|   `-- marts/         # Fact and dimension tables
|-- tests/             # Custom data-quality tests
|-- dbt_project.yml    # Project configuration and materializations
`-- packages.yml       # dbt package dependencies
```

## Technology

dbt Core, SQL, Jinja, and the `dbt-labs/codegen` package.
