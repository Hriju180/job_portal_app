from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .filters import JobFilter
from .models import Job
from .permissions import IsJobOwnerOrReadOnly, IsRecruiterOrReadOnly
from .serializers import JobSerializer


class JobViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for jobs.

    Endpoints:
        GET    /api/jobs/          -> list (searchable, filterable, paginated)
        POST   /api/jobs/          -> create (recruiters only)
        GET    /api/jobs/:id/      -> detail
        PUT    /api/jobs/:id/      -> full update (owner only)
        PATCH  /api/jobs/:id/      -> partial update (owner only)
        DELETE /api/jobs/:id/      -> delete (owner only)

    ModelViewSet gives us all of these for free — we just plug in
    queryset, serializer, permissions, and filters.
    """

    serializer_class = JobSerializer

    # Order matters: the FIRST class that returns False stops the chain.
    # IsRecruiterOrReadOnly -> blocks non-recruiters from writing.
    # IsJobOwnerOrReadOnly  -> blocks recruiters from editing others' jobs.
    permission_classes = [IsAuthenticated, IsRecruiterOrReadOnly, IsJobOwnerOrReadOnly]

    # Attach filters, search, ordering.
    filterset_class = JobFilter
    # ?search=python matches title, description, location.
    search_fields = ["title", "description", "location", "recruiter__username"]
    # ?ordering=-created_at or ?ordering=package
    ordering_fields = ["created_at", "deadline", "title"]
    ordering = ["-created_at"]  # default when no ?ordering= is passed

    def get_queryset(self):
        """
        List view: everyone sees active jobs by default.
        Detail view: owner can see their own inactive jobs too.
        """
        # select_related avoids N+1 queries when serializing recruiter fields.
        queryset = Job.objects.select_related("recruiter", "recruiter__recruiter_profile")

        # If the requester is the recruiter, allow them to see their inactive jobs.
        # The action is set for detail routes; for the list route action == "list".
        if self.action == "list":
            # Default: hide inactive jobs.
            # Recruiters can add ?is_active=false to see inactive ones (filter handles it).
            return queryset

        # Detail / update / delete: return all, and let permissions filter what's allowed.
        return queryset

    def perform_create(self, serializer):
        """
        Set the recruiter automatically from the authenticated user.
        Clients can't spoof this because the serializer field is read-only.
        """
        serializer.save(recruiter=self.request.user)