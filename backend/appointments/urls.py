from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet

router = DefaultRouter()
router.register(r'', AppointmentViewSet, basename='appointment')  # Empty string registration

urlpatterns = [
    path('', include(router.urls)),  # Inherits the 'api/appointments/' prefix
]