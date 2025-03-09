from django.core.management.base import BaseCommand
from django.conf import settings
from django_tenants.utils import schema_context, get_public_schema_name
from tenants.models import Tenant, Domain

class Command(BaseCommand):
    help = 'Create public tenant'

    def handle(self, *args, **options):
        with schema_context(get_public_schema_name()):
            try:
                # Check if public tenant exists
                public_tenant = Tenant.objects.filter(schema_name=get_public_schema_name()).first()
                
                if not public_tenant:
                    # Create public tenant
                    public_tenant = Tenant.objects.create(
                        schema_name=get_public_schema_name(),
                        name='Public',
                        paid_until=None
                    )
                    self.stdout.write(self.style.SUCCESS('Public tenant created successfully'))
                    
                    # Create domain for public tenant
                    domain_name = settings.DEVELOPMENT_DOMAIN if settings.IS_DEVELOPMENT else settings.PUBLIC_DOMAIN_NAME
                    Domain.objects.get_or_create(
                        domain=domain_name,
                        tenant=public_tenant,
                        is_primary=True
                    )
                    self.stdout.write(self.style.SUCCESS(f'Public domain created successfully: {domain_name}'))
                else:
                    self.stdout.write(self.style.SUCCESS('Public tenant already exists'))
                    
                    # Update domain if needed
                    domain_name = settings.DEVELOPMENT_DOMAIN if settings.IS_DEVELOPMENT else settings.PUBLIC_DOMAIN_NAME
                    domain, created = Domain.objects.get_or_create(
                        tenant=public_tenant,
                        is_primary=True,
                        defaults={'domain': domain_name}
                    )
                    
                    # Update domain if it exists but with different name
                    if not created and domain.domain != domain_name:
                        domain.domain = domain_name
                        domain.save()
                        self.stdout.write(self.style.SUCCESS(f'Public domain updated to: {domain_name}'))
                    elif created:
                        self.stdout.write(self.style.SUCCESS(f'Public domain created: {domain_name}'))
                    else:
                        self.stdout.write(self.style.SUCCESS('Public domain already exists and is correct'))
                        
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))