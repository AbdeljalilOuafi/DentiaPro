# records/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'procedure-categories', views.ProcedureCategoryViewSet, basename='procedurecategory')
router.register(r'procedure-types', views.ProcedureTypeViewSet, basename='proceduretype')
router.register(r'procedures', views.ProcedureViewSet, basename='procedure')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]