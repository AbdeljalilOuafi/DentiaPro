#!/usr/bin/env python3
"""create-public module"""
import os
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")  

django.setup()

from django_tenants.utils import get_public_schema_name
from tenants.models import Tenant, Domain
from users.models import User

user = User.objects.create_user(
    email="public@gmail.com",
    password="testpass123",
    first_name="public",
    last_name="schema",
    clinic_name="Untitled Clinic",
    is_paid=True,
    is_verified=True #Email verification
)

tenant = Tenant.objects.create(
    schema_name=f"tenant_{user.id}",
    name='Dental Clinic 1',
    user=user,
    is_verified=True,
    paid_until=None
)

Domain.objects.create(
    domain='localhost',  # I hope i remember to update this to the production domain
    tenant=tenant,
    is_primary=True
)
