from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet

router = DefaultRouter()
router.register(r'', AppointmentViewSet, basename='appointment')  # /api/appointments/ is defined in core.urls and includes this file

urlpatterns = router.urls