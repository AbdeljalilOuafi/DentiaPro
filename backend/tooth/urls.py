from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


urlpatterns = [
    # Matches /api/teeth/en/ or /api/teeth/fr/ (list view)
    path(
        '<str:lang_code>/',
        views.ToothViewSet.as_view({'get': 'list'}),
        name='tooth-list-lang'
    ),
    # Matches /api/teeth/en/UUID/ or /api/teeth/fr/UUID/ (detail view)
    path(
        '<str:lang_code>/<uuid:pk>/',
        views.ToothViewSet.as_view({'get': 'retrieve'}),
        name='tooth-detail-lang'
    ),
    # Optional: Redirect or default view if no language code is provided
    # path('', views.ToothViewSet.as_view({'get': 'list'}), name='tooth-list-default'), # Or redirect
]
