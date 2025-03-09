from rest_framework.permissions import BasePermission

class CanManageUsers(BasePermission):
    # format for user.has_perm is appname.action_modelname
    # user will have these permission based on his role. at this point only Admin role can manage users
    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.has_perm('users.view_user')
        elif request.method == 'POST':
            return request.user.has_perm('users.add_user')
        elif request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('users.change_user')
        elif request.method == 'DELETE':
            return request.user.has_perm('users.delete_user')