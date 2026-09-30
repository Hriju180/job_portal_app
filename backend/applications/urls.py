from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ApplicationViewSet

# Router generates:
#   GET    /
#   POST   /
#   GET    /:id/
#   DELETE /:id/
#   PATCH  /:id/status/
#   GET    /job/:job_id/
router = DefaultRouter()
router.register(r"", ApplicationViewSet, basename="application")

urlpatterns = [
    path("", include(router.urls)),
]