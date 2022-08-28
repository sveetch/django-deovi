import datetime
from pathlib import Path

from django.utils import timezone

import factory

from ..models import MediaFile


class MediaFileFactory(factory.django.DjangoModelFactory):
    """
    Factory to create instance of a MediaFile.

    The factory does not validate you are given a proper absolute file path to 'path'
    attribute since it deduces almost all other attributes from path, you better to
    ensure you give it right.
    """
    title = ""
    path = factory.Faker("file_path", depth=3, category="video", absolute=True)
    filesize = factory.Faker("random_int", min=128, max=40960)

    class Meta:
        model = MediaFile

    @factory.lazy_attribute
    def absolute_dir(self):
        """
        Return absolute directory from 'path' attribute value.

        Returns:
            string: Absolute directory path.
        """
        return str(Path(self.path).parent)

    @factory.lazy_attribute
    def directory(self):
        """
        Return file parent directory name from 'path' attribute value.

        Returns:
            string: Directory name.
        """
        return str(Path(self.path).parent.name)

    @factory.lazy_attribute
    def filename(self):
        """
        Return filename from 'path' attribute value.

        Returns:
            string: Filename.
        """
        return str(Path(self.path).name)

    @factory.lazy_attribute
    def container(self):
        """
        Return file extension from 'path' attribute value.

        Returns:
            string: File extension without leading dot.
        """
        return str(Path(self.path).suffix)[1:]

    @factory.lazy_attribute
    def stored_date(self):
        """
        Return current date.

        Returns:
            datetime.datetime: Current time.
        """
        return timezone.now()
