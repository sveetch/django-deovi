"""
=====================
Media API serializers
=====================

"""
from rest_framework import serializers

from ..models import MediaFile


class MediaFileSerializer(serializers.ModelSerializer):
    """
    Complete representation for detail and writing usage.
    """
    id = serializers.ReadOnlyField()

    class Meta:
        model = MediaFile
        fields = '__all__'
        extra_kwargs = {
            # DRF does not consider fields with ``blank=True`` and ``default=""`` as
            # required
            # TODO: This miss a lot of required files
            "path": {
                "required": True
            },
        }
