with source as (

    select * from{{ source('northwind','Customer') }}
)

select * from source


