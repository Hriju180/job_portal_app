"""
Custom DRF permissions.
Each class returns True to allow or False to reject (403).
"""
from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    """Only authenticated users with role='student' may proceed."""

    message = "Only students can access this resource."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "student"
        )


class IsRecruiter(BasePermission):
    """Only authenticated users with role='recruiter' may proceed."""

    message = "Only recruiters can access this resource."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "recruiter"
        )