from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Customize how User appears in the Django admin panel."""

    list_display = ("email", "username", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("email", "username")
    ordering = ("email",)

    # Add `role` to the detail edit page.
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Role Info", {"fields": ("role",)}),
    )

    # Add `email` and `role` to the "create new user" page.
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Role Info", {"fields": ("email", "role")}),
    )


from .models import User, StudentProfile, RecruiterProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "college", "degree", "graduation_year", "cgpa")
    # Double underscore navigates relations: user__email = User.email.
    search_fields = ("user__email", "college", "degree")


@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company_name", "designation")
    search_fields = ("user__email", "company_name")