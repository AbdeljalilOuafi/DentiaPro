from rest_framework import serializers
from .models import Category, InventoryItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class InventoryItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            'id', 'category', 'category_name', 'name', 'description',
            'quantity', 'unit', 'minimum_quantity', 'cost_price',
            'created_at', 'updated_at', 'expiry_date', 'selling_price'
        ]
        read_only_fields = ['created_at', 'updated_at']