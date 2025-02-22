from django.db import models

# Create your models here.

# No need to create custom permissions yet! 
# Django automatically creates these for the Appointment model:
# - appointment.view_appointment
# - appointment.add_appointment
# - appointment.change_appointment
# - appointment.delete_appointment


# Simple Permission Check in a View:

# rest_framework.permissions import BasePermission

# class CanManageAppointments(BasePermission):
#     def has_permission(self, request, view):
#         if request.method == 'GET':
#             return request.user.has_perm('appointment.view_appointment') # We assign permissions based on the user role in the first user creation
#         elif request.method == 'POST':
#             return request.user.has_perm('appointment.add_appointment')

# class AppointmentViewSet(viewsets.ModelViewSet):
#     permission_classes = [CanManageAppointments]