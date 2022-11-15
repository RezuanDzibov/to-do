from django.http import HttpRequest
from rest_framework import permissions


class IsActive(permissions.BasePermission):
    def has_permission(self, request: HttpRequest, view) -> bool:
        return bool(request.user and request.user.is_active)


class IsStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS or
            request.user and
            request.user.is_authenticated and
            request.user.is_staff
        )
