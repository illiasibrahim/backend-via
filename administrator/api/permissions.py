from rest_framework import permissions

class IsSuperUser(permissions.BasePermission):
    def has_permission(self,request,view):
        try:
            return request.user.is_super_admin
        except:
            return False