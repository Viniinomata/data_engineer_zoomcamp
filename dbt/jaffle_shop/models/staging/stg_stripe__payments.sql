select 
    orderid as order_id,
    paymentmethod,
    status,
    amount
from raw.stripe.payment