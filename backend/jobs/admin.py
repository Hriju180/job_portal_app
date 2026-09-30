from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "recruiter", "location", "job_type", "is_active", "created_at")
    list_filter = ("job_type", "is_active", "location")
    search_fields = ("title", "description", "recruiter__email")
    # Read-only dates so admins don't accidentally edit them.
    readonly_fields = ("created_at", "updated_at")