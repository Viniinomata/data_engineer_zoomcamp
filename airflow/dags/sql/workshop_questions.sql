-- name: date_range
SELECT
    MIN(trip_pickup_date_time) AS earliest_trip,
    MAX(trip_pickup_date_time) AS latest_trip
FROM taxi_trips;

-- name: payment_types
SELECT
    payment_type,
    COUNT(*) AS trips
FROM taxi_trips
GROUP BY payment_type
ORDER BY trips DESC;

-- name: credit_card_percentage
SELECT
    100.0 * COUNT(*) FILTER (
        WHERE lower(trim(payment_type)) = 'credit card'
    )
        / COUNT(*) AS credit_card_percentage
FROM taxi_trips;

-- name: total_tips
SELECT SUM(tip_amt) AS total_tips
FROM taxi_trips;
