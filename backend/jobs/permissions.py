from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsRecruiterOrReadOnly(BasePermission):
    """
    - Anyone authenticated can READ (GET, HEAD, OPTIONS).
    - Only recruiters can WRITE (POST, PUT, PATCH, DELETE).
    """

    message = "Only recruiters can modify job posts."

    def has_permission(self, request, view):
        # SAFE_METHODS = ("GET", "HEAD", "OPTIONS")
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Write methods -> must be an authenticated recruiter.
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "recruiter"
        )


class IsJobOwnerOrReadOnly(BasePermission):
    """
    Object-level check.
    - Anyone authenticated can read.
    - Only the recruiter who created the job can edit/delete it.
    """

    message = "You can only modify your own job posts."

    def has_object_permission(self, request, view, obj):
        # Reads are always fine for authenticated users.
        if request.method in SAFE_METHODS:
            return True

        # Writes -> requester must be the job's recruiter.
        return obj.recruiter == request.user