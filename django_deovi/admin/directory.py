"""
Directory admin interface
"""
from django.contrib import admin

from smart_media.admin import SmartModelAdmin

from ..models import Directory


@admin.register(Directory)
class DirectoryAdmin(SmartModelAdmin):
    list_display = (
        "path",
        "title",
        "device",
        "created_date",
        "last_update",
    )
    list_filter = ("device", "created_date", "last_update")
    search_fields = ["path", "title"]
