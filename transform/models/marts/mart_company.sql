select
    cui,
    company_name,
    brand,
    county,
    locality,
    address,
    website,
    segment,
    caen,
    caen_label
from {{ ref('stg_companies') }}
