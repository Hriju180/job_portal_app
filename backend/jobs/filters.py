import django_filters
from .models import Job


class JobFilter(django_filters.FilterSet):
    """
    Query-param filters for GET /api/jobs/.
    Usage: /api/jobs/?job_type=intern&location=Bangalore&is_active=true
    """

    # Exact match on job type.
    job_type = django_filters.CharFilter(field_name="job_type", lookup_expr="exact")

    # Case-insensitive substring match on location.
    # ?location=bang -> matches "Bangalore"
    location = django_filters.CharFilter(field_name="location", lookup_expr="icontains")

    # Substring match on title — handy for "python developer" queries.
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")

    # Boolean filter to show only active / inactive posts.
    is_active = django_filters.BooleanFilter(field_name="is_active")

    # Deadline range filters (bonus, easy to add).
    deadline_after = django_filters.DateFilter(field_name="deadline", lookup_expr="gte")
    deadline_before = django_filters.DateFilter(field_name="deadline", lookup_expr="lte")

    class Meta:
        model = Job
        # Explicitly list fields that can be filtered via query params.
        fields = ["job_type", "location", "title", "is_active"]