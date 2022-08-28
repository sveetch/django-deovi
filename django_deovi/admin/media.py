"""
Media admin interface
"""
from django.contrib import admin

from ..models import MediaFile


class MediaFileAdmin(admin.ModelAdmin):
    pass


# Registering interface to model
admin.site.register(MediaFile, MediaFileAdmin)
