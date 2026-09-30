from django.conf import settings
from django.db import models

from jobs.models import Job


class Application(models.Model):
    """
    A student's application to a specific job.
    Tracks status through a fixed pipeline.
    """

    class Status(models.TextChoices):
        # Order here is informational — the actual pipeline is:
        # APPLIED -> SHORTLISTED -> INTERVIEW -> SELECTED / REJECTED
        APPLIED = "applied", "Applied"
        SHORTLISTED = "shortlisted", "Shortlisted"
        INTERVIEW = "interview", "Interview"
        SELECTED = "selected", "Selected"
        REJECTED = "rejected", "Rejected"

    # Who applied. Deleting the student deletes their applications.
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications",
    )

    # Which job. Deleting the job removes all its applications too.
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications",
    )

    # Current stage in the pipeline. Only recruiters can change this.
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.APPLIED
    )

    # Snapshot of the student's resume AT THE TIME OF APPLYING.
    # If the student later replaces their resume, this stays frozen —
    # recruiters always see the version the student submitted.
    resume = models.FileField(upload_to="applications/", blank=True, null=True)

    # Optional note the student writes when applying.
    cover_note = models.TextField(blank=True)

    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Prevent the same student from applying to the same job twice.
        # Enforced at the database level (not just the serializer).
        unique_together = ("student", "job")
        # Newest applications first by default.
        ordering = ["-applied_at"]

    def __str__(self):
        return f"{self.student.email} -> {self.job.title} ({self.status})"