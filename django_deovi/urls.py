"""
Application URLs
"""
from django.urls import path, include

from .views import (
    DeviceIndexView, DeviceDetailView, DirectoryDetailView,
)
from .routers import router


app_name = "django_deovi"


urlpatterns = [
    path("", DeviceIndexView.as_view(), name="device-index"),
    path("api/", include(router.urls)),
    path(
        "<slug:device_slug>/",
        DeviceDetailView.as_view(),
        name="device-detail"
    ),
    path(
        "<slug:device_slug>/<slug:directory_pk>/",
        DirectoryDetailView.as_view(),
        name="directory-detail"
    ),
]
