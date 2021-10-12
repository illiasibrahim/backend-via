from rest_framework import permissions

from rider_app.models import Task, Bucket
from rider_app.models import Rider

class IsRider(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            return request.user.is_rider
        except:
            return False

class IsHubRider(permissions.BasePermission):
    def has_object_permission(self, request, view,obj):
        try:
            rider = Rider.objects.get(account = request.user)
            return obj.hub == rider.hub
        except:
            return False

class IsAssignedRider(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            if (isinstance(obj, Task)):
                return obj.rider.account == request.user
            elif (isinstance(obj, Bucket)):
                return obj.rider.account == request.user
        except:
            return False

class IsInactiveRider(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            rider = Rider.objects.get(account = request.user)
            return rider.hub is None
        except:
            return False

class IsActiveRider(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            rider = Rider.objects.get(account = request.user)
            return rider.hub is not None
        except:
            return False