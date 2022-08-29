"""
Directory admin interface
"""
from django.contrib import admin

from ..models import Directory


class DirectoryAdmin(admin.ModelAdmin):
    pass


# Registering interface to model
admin.site.register(Directory, DirectoryAdmin)
