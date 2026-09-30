"""
API views for authentication.
Each view is a class; DRF calls the method matching the HTTP verb.
"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


# Enables multipart/form-data file uploads.
from rest_framework.parsers import MultiPartParser, FormParser

from .models import StudentProfile, RecruiterProfile
from .permissions import IsStudent, IsRecruiter


from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    get_tokens_for_user,

    StudentProfileSerializer,
    RecruiterProfileSerializer,
    ResumeUploadSerializer,
)


User = get_user_model()


class RegisterView(APIView):
    """POST /api/auth/register/ — create a new user and return JWT tokens."""
    # AllowAny overrides the project default (which requires authentication).
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # raises -> 400 on invalid
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        return Response(
            {"user": UserSerializer(user).data, **tokens},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """POST /api/auth/login/ — verify credentials, return tokens."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        tokens = get_tokens_for_user(user)
        return Response({"user": UserSerializer(user).data, **tokens})


class MeView(APIView):
    """GET /api/auth/me/ — return the current authenticated user."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class LogoutView(APIView):
    """POST /api/auth/logout/ — client-side logout (drop tokens)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # With stateless JWT, "logout" means the client deletes their tokens.
        # If you enable token blacklisting later, blacklist the refresh here.
        return Response({"detail": "Logged out."})


class PasswordResetRequestView(APIView):
    """POST /api/auth/password-reset/ — email a reset link to the user."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = User.objects.get(email=email)

        # Build the reset link: base64(user_id)/token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"

        # Console email backend prints this to the terminal in dev.
        send_mail(
            subject="Password Reset Request",
            message=f"Click to reset your password: {reset_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return Response({"detail": "Reset link sent to your email."})


class PasswordResetConfirmView(APIView):
    """POST /api/auth/password-reset-confirm/ — apply the new password."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password reset successful."})


class StudentProfileView(APIView):
    """
    GET  /api/auth/profile/student/  -> fetch current student's profile
    PUT  /api/auth/profile/student/  -> update it
    """
    # Both must pass -> authenticated AND a student.
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        # get_or_create as a safety net for users created before the signal.
        profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        return Response(StudentProfileSerializer(profile).data)

    def put(self, request):
        profile, _ = StudentProfile.objects.get_or_create(user=request.user)

        # partial=True -> accepts partial payloads (behaves like PATCH too).
        serializer = StudentProfileSerializer(
            profile, data=request.data, partial=True
        )
        # raise_exception=True -> 400 on invalid data, no manual checking.
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class RecruiterProfileView(APIView):
    """
    GET  /api/auth/profile/recruiter/
    PUT  /api/auth/profile/recruiter/
    """
    permission_classes = [IsAuthenticated, IsRecruiter]

    def get(self, request):
        profile, _ = RecruiterProfile.objects.get_or_create(user=request.user)
        return Response(RecruiterProfileSerializer(profile).data)

    def put(self, request):
        profile, _ = RecruiterProfile.objects.get_or_create(user=request.user)
        serializer = RecruiterProfileSerializer(
            profile, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ResumeUploadView(APIView):
    """
    POST /api/auth/profile/resume/  -> upload a student's PDF resume.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    # Without these parsers DRF would reject multipart uploads.
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        # Validates PDF + size <= 5 MB.
        serializer = ResumeUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile, _ = StudentProfile.objects.get_or_create(user=request.user)

        # Assigning a FileField from request.FILES saves the file to disk
        # (MEDIA_ROOT/resumes/...) and stores the relative path in DB.
        profile.resume = serializer.validated_data["resume"]
        profile.save()

        # Return full profile so the frontend can refresh its state.
        return Response(
            StudentProfileSerializer(profile).data,
            status=status.HTTP_200_OK,
        )
