"""
Directory admin interface
"""
from django.contrib import admin

from smart_media.admin import SmartModelAdmin

from ..models import Directory


@admin.register(Directory)
class DirectoryAdmin(SmartModelAdmin):
    pass
