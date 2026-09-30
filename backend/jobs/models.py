from django.conf import settings
from django.db import models


class Job(models.Model):
    """
    A job posting created by a recruiter.
    Students browse these; recruiters CRUD their own.
    """

    class JobType(models.TextChoices):
        # TextChoices enforces valid values + gives us Job.JobType.FULL_TIME.
        FULL_TIME = "full_time", "Full Time"
        INTERN = "intern", "Internship"
        PART_TIME = "part_time", "Part Time"
        CONTRACT = "contract", "Contract"

    # Who posted this job. If recruiter is deleted, delete their jobs too.
    # related_name="jobs" lets us do user.jobs.all() to list a recruiter's postings.
    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="jobs",
    )

    title = models.CharField(max_length=150)
    description = models.TextField()

    location = models.CharField(max_length=100)

    # Dropdown of allowed types; defaults to full-time.
    job_type = models.CharField(
        max_length=20, choices=JobType.choices, default=JobType.FULL_TIME
    )

    # Free text — e.g. "8 LPA", "₹25,000/month". Simpler than structured ranges
    # for MVP and lets recruiters write whatever format fits.
    package = models.CharField(max_length=100, blank=True)

    # JSON list of skill strings: ["Python", "Django"]. Good for keyword matching.
    skills_required = models.JSONField(default=list, blank=True)

    # Application deadline — students shouldn't apply after this.
    deadline = models.DateField(null=True, blank=True)

    # Soft toggle — recruiters can hide a job without deleting it.
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Default ordering for list endpoints: newest first.
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} @ {self.recruiter.username}"