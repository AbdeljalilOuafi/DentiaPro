from django_tenants.models import Domain
from customers.models import Client

# Get public tenant
public_tenant = Client.objects.get(schema_name='public')

# Check current domains
current_domains = Domain.objects.filter(tenant=public_tenant)
print("Current public domains:", [d.domain for d in current_domains])

# If you need to update/create the correct domain
Domain.objects.filter(tenant=public_tenant).delete()  # Remove any existing domains
Domain.objects.create(
    domain='www.crafitori.com',
    tenant=public_tenant,
    is_primary=True
)