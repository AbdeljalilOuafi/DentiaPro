from django.db import transaction
from django.dispatch import receiver
from django_tenants.signals import post_schema_sync
from django_tenants.utils import schema_context
from .models import Category, InventoryItem
from .inventory_data import inventory_data
import logging

logger = logging.getLogger(__name__)

@receiver(post_schema_sync)
def create_initial_inventory_data(sender, tenant, **kwargs):
    logger.info("Signal was activated...")
    with schema_context(tenant.schema_name):
        logger.info(f"Schema_name: {tenant.schema_name}")
        for data in inventory_data:
            category_data = data.get('category', 'N/A')
            items = data.get('items', [])
            
            category, _ = Category.objects.get_or_create(tenant=tenant, **category_data)
            logger.info(f"Created {category}")
            inventory_items = [InventoryItem(tenant=tenant, category=category, name=item) for item in items]
            
            if inventory_items:
                logger.info(f"Adding {inventory_items}")
                InventoryItem.objects.bulk_create(inventory_items)
            else:
                logger.info(f"No inventory_items are being added")
    transaction.on_commit(create_initial_inventory_data)