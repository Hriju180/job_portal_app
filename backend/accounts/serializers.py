"""
Serializers convert between Python objects (models) and JSON.
They also do validation.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Read-only representation of a user (used for /me and login responses)."""

    class Meta:
        model = User
        # Only expose safe fields — never password or permissions here.
        fields = ("id", "email", "username", "first_name", "last_name", "role")
        read_only_fields = ("id", "email", "role")


class RegisterSerializer(serializers.ModelSerializer):
    """Handles user registration."""

    # write_only=True -> accepts the input but never returns it in responses.
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("email", "username", "password", "password2", "role")

    def validate(self, attrs):
        """Object-level validation (runs after field validation)."""
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        # Prevent anyone from self-registering as admin.
        if attrs.get("role") == User.Role.ADMIN:
            raise serializers.ValidationError({"role": "Cannot register as admin."})
        return attrs

    def create(self, validated_data):
        # Drop password2 — not a real field on the User model.
        validated_data.pop("password2")
        password = validated_data.pop("password")

        # Use set_password to hash the password (never store plaintext).
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Validates login credentials and attaches the user to validated_data."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        from django.contrib.auth import authenticate
        # authenticate() checks the password hash in the DB.
        user = authenticate(
            request=self.context.get("request"),
            username=attrs["email"],   # our USERNAME_FIELD is email
            password=attrs["password"],
        )
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled.")
        attrs["user"] = user
        return attrs


def get_tokens_for_user(user):
    """Helper to produce access + refresh JWT pair for a user."""
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user with this email.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, attrs):
        # Decode the base64 uid back into a user ID.
        try:
            uid = force_str(urlsafe_base64_decode(attrs["uid"]))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            raise serializers.ValidationError("Invalid reset link.")

        # Verify the token is still valid (default: 3 days).
        if not default_token_generator.check_token(user, attrs["token"]):
            raise serializers.ValidationError("Invalid or expired token.")

        attrs["user"] = user
        return attrs

    def save(self):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user




from .models import StudentProfile, RecruiterProfile


class StudentProfileSerializer(serializers.ModelSerializer):
    """
    Converts StudentProfile <-> JSON.
    Two read-only fields pull from the related User.
    """

    # source="user.email" traverses the OneToOne to reach the User's email.
    email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = StudentProfile
        fields = (
            "id", "email", "username",
            "phone", "bio", "resume",
            "degree", "college", "cgpa", "graduation_year", "skills",
            "updated_at",
        )
        # These fields can't be changed through this serializer.
        # Resume is handled by a dedicated upload endpoint.
        read_only_fields = ("id", "email", "username", "resume", "updated_at")


class RecruiterProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = RecruiterProfile
        fields = (
            "id", "email", "username",
            "company_name", "company_website", "company_logo", "designation",
            "updated_at",
        )
        read_only_fields = ("id", "email", "username", "updated_at")


class ResumeUploadSerializer(serializers.Serializer):
    """
    Plain Serializer — we only validate the file.
    The view saves it onto the StudentProfile.
    """

    resume = serializers.FileField()

    def validate_resume(self, value):
        """
        DRF calls validate_<fieldname> automatically.
        Raising ValidationError -> 400 with the message.
        """
        # value.name is the original filename (e.g. "resume.pdf").
        if not value.name.lower().endswith(".pdf"):
            raise serializers.ValidationError("Only PDF files are allowed.")

        # value.size is in bytes. 5 MB cap.
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 5 MB.")

        return value