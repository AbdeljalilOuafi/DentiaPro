
from rest_framework.permissions import BasePermission
class CanManageAppointments(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.has_perm('appointments.view_appointment')
        elif request.method == 'POST':
            return request.user.has_perm('appointments.add_appointment')
        elif request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('appointments.change_appointment')
        elif request.method == 'DELETE':
            return request.user.has_perm('appointments.delete_appointment')
        return False
