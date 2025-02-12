#!/usr/bin/env python3
"""create-tenant module"""


from tenants.models import Client, Domain

# Create a new tenant
tenant = Client(
    schema_name="dentist1", # we could use argv here ?
    name="Dentist 1",
    paid_until="2025-01-01",
    on_trial=True,
    is_verified=False,  # Will change after payment
)
tenant.save()  # This automatically creates the schema in the database

# Assign a domain and Creates a Foreign key relationship with the tenant.
# When a request comes in, django-tanant-schema Middleware intercepts the domain which the request is coming from.
# It then queries the Domain table to acceess the schema name on the tanant object (schema = domain.tenant.schema_name)
# PostgresSQL sets the schema to be the schema_name and will be used for querying for the entire request lifetime
# this ensures that each subdomain will have its own schema/isolated tables 
domain = Domain(domain="dentist1.yoursaas.com", tenant=tenant)
domain.save()