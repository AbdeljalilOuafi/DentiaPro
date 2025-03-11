from rest_framework.permissions import BasePermission
import logging

logger = logging.getLogger(__name__)

class CanManageUsers(BasePermission):
    # format for user.has_perm is appname.action_modelname
    # user will have these permission based on his role. at this point only Admin role can manage users
    def has_permission(self, request, view):
        logger.info(f"Checking permissions for user: {request.user}")
        logger.info(f"Method: {request.method}")
        logger.info(f"All permissions: {request.user.get_all_permissions()}")

        if request.method == 'GET':
            has_perm = request.user.has_perm('users.view_user')
            logger.info(f"Checking users.view_user permission: {has_perm}")
            return has_perm

        elif request.method == 'POST':
            return request.user.has_perm('users.add_user')
        elif request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('users.change_user')
        elif request.method == 'DELETE':
            return request.user.has_perm('users.delete_user')