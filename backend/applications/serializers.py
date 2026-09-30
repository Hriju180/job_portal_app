from django.utils import timezone
from rest_framework import serializers

from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for applications.
    Adds read-only convenience fields and enforces business rules.
    """

    # Read-only fields pulled from related objects so clients get richer data
    # without extra round trips.
    student_email = serializers.EmailField(source="student.email", read_only=True)
    student_username = serializers.CharField(source="student.username", read_only=True)
    job_id = serializers.IntegerField(source="job.id", read_only=True)
    job_title = serializers.CharField(source="job.title", read_only=True)
    job_company = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = (
            "id",
            "student", "student_email", "student_username",
            "job", "job_id", "job_title", "job_company",
            "status",
            "resume",
            "cover_note",
            "applied_at", "updated_at",
        )
        # These can only be set server-side, never by the client.
        # - student: set from request.user
        # - status:  changed only via the recruiter's status endpoint
        # - resume:  copied from the student's profile at apply time
        read_only_fields = (
            "id", "student", "status", "resume",
            "applied_at", "updated_at",
        )

    def get_job_company(self, obj):
        """Return the company name of the recruiter who posted this job."""
        profile = getattr(obj.job.recruiter, "recruiter_profile", None)
        return profile.company_name if profile else None

    def validate_job(self, value):
        """
        Runs when the `job` field is supplied (i.e., on create).
        Business rules for what jobs a student is allowed to apply to.
        """
        if not value.is_active:
            raise serializers.ValidationError(
                "This job is no longer accepting applications."
            )
        if value.deadline and value.deadline < timezone.now().date():
            raise serializers.ValidationError("Application deadline has passed.")
        return value

    def validate(self, attrs):
        """
        Cross-field validation. On create we need to ensure:
        1. The student has uploaded a resume.
        2. They haven't already applied to this job.
        """
        request = self.context.get("request")
        if not (request and request.user.is_authenticated):
            return attrs

        # Only enforce these on create (PATCH/PUT aren't allowed for this serializer).
        if self.instance is None:
            # Fetch the student's profile; if missing, treat as no resume.
            profile = getattr(request.user, "student_profile", None)
            if not profile or not profile.resume:
                raise serializers.ValidationError(
                    "Please upload a resume before applying."
                )

            job = attrs.get("job")
            if job and Application.objects.filter(
                student=request.user, job=job
            ).exists():
                raise serializers.ValidationError(
                    "You have already applied to this job."
                )
        return attrs