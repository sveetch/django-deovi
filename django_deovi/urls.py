"""
Application URLs
"""
from django.urls import path, include

from .views import DeviceIndexView, MediaFileDetailView
from .routers import router


app_name = "django_deovi"


urlpatterns = [
    path("", DeviceIndexView.as_view(), name="device-index"),
    path("api/", include(router.urls)),
    path(
        "<int:mediafile_pk>/",
        MediaFileDetailView.as_view(),
        name="mediafile-detail"
    ),
]
