from haystack import indexes

from .models import Device, MediaFile
from .search_fields import EdgeNgramField


class DeviceIndex(indexes.SearchIndex, indexes.Indexable):
    text = EdgeNgramField(
        document=True,
        use_template=True,
        template_name="django_deovi/search/directory_indexes_template.txt"
    )

    def get_model(self):
        return Device


class MediaFileIndex(indexes.SearchIndex, indexes.Indexable):
    text = EdgeNgramField(
        document=True,
        use_template=True,
        template_name="django_deovi/search/mediafile_indexes_template.txt"
    )

    def get_model(self):
        return MediaFile
