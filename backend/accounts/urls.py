from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    LoginView,
    MeView,
    LogoutView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    
    StudentProfileView,
    RecruiterProfileView,
    ResumeUploadView,
)

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("refresh/", TokenRefreshView.as_view()),   # built-in refresh view
    path("me/", MeView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("password-reset/", PasswordResetRequestView.as_view()),
    path("password-reset-confirm/", PasswordResetConfirmView.as_view()),

    path("profile/student/", StudentProfileView.as_view()),
    path("profile/recruiter/", RecruiterProfileView.as_view()),
    # Separate endpoint because file upload needs different parsers.
    path("profile/resume/", ResumeUploadView.as_view()),
]


