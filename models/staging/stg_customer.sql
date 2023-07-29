with source as (

    select * from{{ source('northwind','Customer') }}
)

select 
    *,
    current_timestamp() as ingestion_timestamp
from source


