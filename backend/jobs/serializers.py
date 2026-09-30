from rest_framework import serializers

from .models import Job


class JobSerializer(serializers.ModelSerializer):
    """
    Serializer for job listings.
    Adds read-only convenience fields from the related recruiter.
    """

    # These pull from the related User; the client cannot change them.
    recruiter_email = serializers.EmailField(
        source="recruiter.email", read_only=True
    )
    recruiter_username = serializers.CharField(
        source="recruiter.username", read_only=True
    )
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = (
            "id",
            "recruiter",             # included read-only (set server-side)
            "recruiter_email",
            "recruiter_username",
            "company_name",
            "title",
            "description",
            "location",
            "job_type",
            "package",
            "skills_required",
            "deadline",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "recruiter",             # always set from request.user, never client
            "created_at",
            "updated_at",
        )

    def get_company_name(self, obj):
        """
        Return the recruiter's company name if their profile exists.
        Safe against a missing profile via getattr default.
        """
        profile = getattr(obj.recruiter, "recruiter_profile", None)
        return profile.company_name if profile else None

    def validate_deadline(self, value):
        """
        Deadline must not be in the past.
        Only enforce on new submissions, not edits to old jobs.
        """
        from django.utils import timezone
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Deadline cannot be in the past.")
        return value

    def validate_skills_required(self, value):
        """Skills must be a list of non-empty strings."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Must be a list of skills.")
        for item in value:
            if not isinstance(item, str) or not item.strip():
                raise serializers.ValidationError("Each skill must be a non-empty string.")
        return value