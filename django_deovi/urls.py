"""
Application URLs
"""
from django.urls import path

from .views import (
    DeviceIndexView, DeviceDetailView, DeviceTreeView, DirectoryDetailView,
    DeviceTreeExportView,
)


app_name = "django_deovi"


urlpatterns = [
    path("", DeviceIndexView.as_view(), name="device-index"),
    path(
        "<slug:device_slug>/",
        DeviceDetailView.as_view(),
        name="device-detail"
    ),
    path(
        "<slug:device_slug>/tree/",
        DeviceTreeView.as_view(),
        name="device-tree"
    ),
    path(
        "<slug:device_slug>/tree/export/",
        DeviceTreeExportView.as_view(),
        name="device-tree-export"
    ),
    path(
        "<slug:device_slug>/<slug:directory_pk>/",
        DirectoryDetailView.as_view(),
        name="directory-detail"
    ),
]
