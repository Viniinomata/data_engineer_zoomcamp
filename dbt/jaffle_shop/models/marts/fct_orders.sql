select 
    ord.order_id,
    ord.customer_id,
    ord.order_date,
    pay.amount
from {{ ref('stg_jaffle_shop__orders') }} as ord
left join {{ ref('stg_stripe__payments') }} as pay using (order_id)
where pay.status = 'success'