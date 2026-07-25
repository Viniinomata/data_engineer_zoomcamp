select 
    order_id,
    sum(amount) as total_payment_amount
from {{ ref('stg_stripe__payments') }}
group by 1
having sum(amount) < 0