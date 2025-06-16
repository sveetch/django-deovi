from haystack import indexes

from .models import Directory, MediaFile
from .search_fields import EdgeNgramField


class DirectoryIndex(indexes.SearchIndex, indexes.Indexable):
    text = EdgeNgramField(
        document=True,
        use_template=True,
        template_name="django_deovi/search/directory_indexes_template.txt"
    )

    def get_model(self):
        return Directory

    def index_queryset(self, using=None):
        """
        Only index directories that have a non empty title.
        """
        return self.get_model().objects.exclude(title="")


class MediaFileIndex(indexes.SearchIndex, indexes.Indexable):
    text = EdgeNgramField(
        document=True,
        use_template=True,
        template_name="django_deovi/search/mediafile_indexes_template.txt"
    )

    def get_model(self):
        return MediaFile
