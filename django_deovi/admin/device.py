"""
Device admin interface
"""
from django.contrib import admin

from ..models import Device


class DeviceAdmin(admin.ModelAdmin):
    pass


# Registering interface to model
admin.site.register(Device, DeviceAdmin)
