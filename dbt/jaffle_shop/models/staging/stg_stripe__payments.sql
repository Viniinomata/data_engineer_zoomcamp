select 
    orderid as order_id,
    paymentmethod as payment_method,
    status,
    amount / 100 as amount,
from {{ source('stripe', 'payment') }}