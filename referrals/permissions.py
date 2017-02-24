from rest_framework import permissions


class IsLoggedIn(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to view it.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated()
