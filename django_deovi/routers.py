"""
Application API URLs
"""
from rest_framework import routers

from .viewsets import MediaFileViewSet


# API router
router = routers.DefaultRouter()

router.register(
    r"files",
    MediaFileViewSet,
    basename="api-mediafile"
)
