"""
=================
MediaFile API views
=================

"""
from rest_framework import viewsets

from ..models import MediaFile
from ..serializers import MediaFileSerializer

# from .mixins import ConditionalResumedSerializerMixin


class MediaFileViewSet(viewsets.ModelViewSet):
    """
    Viewset for all HTTP methods on MediaFile model.
    """
    model = MediaFile
    serializer_class = MediaFileSerializer
    # resumed_serializer_class = MediaFileResumeSerializer

    def get_queryset(self):
        return self.model.objects.all()
