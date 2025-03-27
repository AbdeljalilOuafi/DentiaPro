# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Category, InventoryItem
from .serializers import CategorySerializer, InventoryItemSerializer
from django.db.models import Q
from utils.pagination import CustomPagination


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination  
    lookup_field = 'pk'

    def get_queryset(self):
        # Filter categories by current tenant
        return Category.objects.filter(tenant=self.request.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)

class InventoryItemViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination  
    lookup_field = 'pk'

    def get_queryset(self):
        queryset = InventoryItem.objects.filter(tenant=self.request.tenant)
        
        # Add search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(category__name__icontains=search)
            )

        # Add category filter
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category_id=category)

        return queryset.select_related('category')

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)