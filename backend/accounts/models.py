from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model.
    Extends AbstractUser so we keep every built-in field (username, password,
    is_staff, is_superuser, etc.) and just add `role`.
    """
    class Role(models.TextChoices):
        # TextChoices gives us User.Role.STUDENT etc., and enforces valid values.
        STUDENT = "student", "Student"
        RECRUITER = "recruiter", "Recruiter"
        ADMIN = "admin", "Admin"

    # Email is unique — we log in with it instead of username.
    email = models.EmailField(unique=True)

    # Role determines what the user can do (enforced in permissions.py).
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)

    # Log in with email instead of username.
    USERNAME_FIELD = "email"

    # Fields required by createsuperuser (excluding USERNAME_FIELD and password).
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.email} ({self.role})"



# --- (User model from Phase 1 stays exactly as-is) ---


# ---------------------------------------------------------------------------
# STUDENT PROFILE
# ---------------------------------------------------------------------------
class StudentProfile(models.Model):
    """
    Extra fields that only students have.
    Lives in a separate table because recruiters don't need resume/CGPA/skills.
    OneToOne -> each User has at most one StudentProfile.
    """

    # on_delete=CASCADE: deleting the User also deletes this profile.
    # related_name lets us do user.student_profile in code.
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="student_profile"
    )

    # blank=True -> optional in forms/serializers.
    phone = models.CharField(max_length=15, blank=True)

    # TextField -> no max length; for longer free-text fields.
    bio = models.TextField(blank=True)

    # FileField: stores the path in DB; uploads go to MEDIA_ROOT/resumes/.
    # null=True + blank=True -> resume is optional at signup.
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)

    degree = models.CharField(max_length=100, blank=True)
    college = models.CharField(max_length=150, blank=True)

    # DecimalField avoids float rounding issues; max 99.99.
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    # Positive integer -> year (e.g. 2026).
    graduation_year = models.PositiveIntegerField(null=True, blank=True)

    # JSONField stores a Python list like ["Python", "Django"] as native JSON.
    # default=list -> every row starts with an empty list, never None.
    skills = models.JSONField(default=list, blank=True)

    # auto_now_add: set once on creation.
    created_at = models.DateTimeField(auto_now_add=True)
    # auto_now: updated on every .save().
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} (Student)"


# ---------------------------------------------------------------------------
# RECRUITER PROFILE
# ---------------------------------------------------------------------------
class RecruiterProfile(models.Model):
    """
    Extra fields that only recruiters have.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="recruiter_profile"
    )

    # blank=True so the profile can be auto-created empty on signup.
    company_name = models.CharField(max_length=150, blank=True)

    # URLField validates format.
    company_website = models.URLField(blank=True)

    # ImageField -> Pillow required. Stores path in DB, image in media/logos/.
    company_logo = models.ImageField(upload_to="logos/", blank=True, null=True)

    designation = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} ({self.company_name})"