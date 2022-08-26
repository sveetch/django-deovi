"""
Application URLs
"""
from django.urls import path, include

from .views import MediaFileDetailView
from .routers import router


app_name = "django_deovi"


urlpatterns = [
    # path("", MediaFileIndexView.as_view(), name="mediafile-index"),
    path("api/", include(router.urls)),
    path(
        "<int:mediafile_pk>/",
        MediaFileDetailView.as_view(),
        name="mediafile-detail"
    ),
]
