from django.db import models
from tenants.models import Tenant

class Category(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=100)  # Removed unique=True as it might cause issues across tenants
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        unique_together = ['tenant', 'name']  # This ensures uniqueness per tenant
        verbose_name_plural = "categories"


class InventoryItem(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="inventory_items")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="items")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=20, default='units')  # Added default
    minimum_quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expiry_date = models.DateTimeField(blank=True, null=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Added default
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"

    class Meta:
        ordering = ["name"]
        unique_together = ['tenant', 'name']  # This ensures uniqueness per tenant