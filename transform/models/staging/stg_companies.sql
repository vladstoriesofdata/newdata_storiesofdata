with source as (
    select
        cast(cui as bigint) as cui,
        "Nume" as company_name,
        "Brand" as brand,
        "Localitate" as locality,
        "Adresa" as address,
        "Website" as website,
        "Flag" as segment,
        cast("CAEN" as integer) as caen,
        upper(trim(
            replace(replace(replace(replace(replace(replace(replace(replace(
                coalesce("Jud", ''),
                'ă', 'a'), 'â', 'a'), 'î', 'i'), 'ș', 's'), 'ş', 's'), 'ț', 't'), 'ţ', 't'),
                'Ă', 'A')
        )) as county_folded
    from {{ source('raw', 'info_companii') }}
)

select
    cui,
    company_name,
    brand,
    locality,
    address,
    website,
    segment,
    caen,
    case caen
        when 5610 then 'Restaurante'
        when 1085 then 'Fabricarea de mancaruri preparate'
        else 'CAEN ' || cast(caen as varchar)
    end as caen_label,
    case
        when county_folded is null or county_folded = '' then 'NECUNOSCUT'
        else county_folded
    end as county
from source
