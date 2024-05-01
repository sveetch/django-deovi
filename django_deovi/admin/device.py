"""
Device admin interface
"""
from django.contrib import admin

from ..models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "slug",
        "title",
        "disk_total",
        "disk_used",
        "disk_free",
        "created_date",
        "last_update",
    )
