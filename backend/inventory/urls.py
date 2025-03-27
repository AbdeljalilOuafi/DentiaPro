from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, InventoryItemViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'items', InventoryItemViewSet, basename='inventory-item')

urlpatterns = [
    path('', include(router.urls)),
]