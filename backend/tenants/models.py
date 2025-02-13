from django.db import models

from django_tenants.models import TenantMixin, DomainMixin
from django.db import models
from django.contrib.auth import get_user_model
import uuid


User = get_user_model()

class Tenant(TenantMixin):
    name = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="tenant")
    paid_until = models.DateField(null=True)  
    on_trial = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)  
    
    auto_create_schema = True  # Automatically create schema on save
    

class Domain(DomainMixin):
    pass  # Stores domain/subdomain info


