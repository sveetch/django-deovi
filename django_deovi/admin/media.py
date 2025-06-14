"""
Media admin interface
"""
from django.contrib import admin

from ..models import MediaFile


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = (
        "filename",
        "directory",
        "container",
        "stored_date",
        "loaded_date",
    )
    list_filter = (
        "directory__device",
        "container",
        "stored_date",
        "loaded_date"
    )
    search_fields = ["filename", "path"]
