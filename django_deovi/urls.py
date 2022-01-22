"""
Application URLs
"""
from django.urls import path, include

from .views import (
    BlogIndexView, BlogDetailView,
    ArticleDetailView,
)
from .routers import router


app_name = "django_deovi"


urlpatterns = [
    path("", BlogIndexView.as_view(), name="blog-index"),
    path("api/", include(router.urls)),
    path("<int:blog_pk>/", BlogDetailView.as_view(), name="blog-detail"),
    path(
        "<int:blog_pk>/<int:article_pk>/",
        ArticleDetailView.as_view(),
        name="article-detail"
    ),
]
