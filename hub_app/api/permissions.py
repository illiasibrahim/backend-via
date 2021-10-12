from rest_framework import permissions

from hub_app.models import Hub


class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            return request.user.is_super_admin
        except:
            return False

class IsStaffUser(permissions.BasePermission):
    def has_permission(self,request,view):
        try:
            return request.user.is_staff
        except:
            return False

class IsRequestedStaffUser(permissions.BasePermission):
    def has_object_permission(self,request,view,obj):
        try:
            hub = Hub.objects.get(account = request.user)
            return obj.hub == hub
        except:
            return False

class IsAuthorizedHub(permissions.BasePermission):
    def has_object_permission(self,request,view,obj):
        try:
            hub = Hub.objects.get(account = request.user)
            return obj.hub == hub
        except:
            return False