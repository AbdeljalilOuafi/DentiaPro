#!/usr/bin/env python3
"""create-localhost_domain module"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")  
django.setup()


# management/commands/setup_localhost_domain.py
from django.core.management.base import BaseCommand
from django.db import transaction
from tenants.models import Domain, Tenant 


class Command(BaseCommand):
    help = 'Sets up localhost domain for development'

    def handle(self, *args, **kwargs):
        try:
            with transaction.atomic():
                # Create a public tenant if it doesn't exist
                public_tenant, created = Tenant.objects.get_or_create(
                    schema_name='public',
                    defaults={
                        'name': 'Public Tenant',
                        'paid_until': None
                    }
                )
                
                # Create localhost domain if it doesn't exist
                domain, created = Domain.objects.get_or_create(
                    domain='localhost',
                    defaults={
                        'tenant': public_tenant,
                        'is_primary': True
                    }
                )
                
                # Also add localhost:8000 for development
                domain_8000, created = Domain.objects.get_or_create(
                    domain='localhost:8000',
                    defaults={
                        'tenant': public_tenant,
                        'is_primary': False
                    }
                )
                
                self.stdout.write(
                    self.style.SUCCESS('Successfully set up localhost domains')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error setting up localhost domain: {str(e)}')
            )