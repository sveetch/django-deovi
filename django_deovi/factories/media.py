import datetime
from pathlib import Path

from django.utils import timezone

import factory

from ..dump import DumpedFile
from ..models import MediaFile
from deovi.collector import MEDIAS_CONTAINERS, MEDIAS_DEFAULT_CONTAINER_NAME


class DumpedFileFactory(factory.Factory):
    """
    Factory for a directory child file entry from a dump.

    Do not relate on any Django model.
    """
    path = factory.Faker("file_path", depth=3, category="video", absolute=True)
    size = factory.Faker("random_int", min=128, max=40960)

    class Meta:
        model = DumpedFile

    @factory.lazy_attribute
    def absolute_dir(self):
        """
        Return absolute directory from 'path' attribute value.

        Returns:
            string: Absolute directory path.
        """
        return str(Path(self.path).parent)

    @factory.lazy_attribute
    def relative_dir(self):
        """
        Return a relative path expurged from the very first directory.

        This is tricky since deovi compute the relative_dir from given commandline
        argument basepath, but we omit and therefore it is would be complex to manage it
        correctly.

        Returns:
            string: Directory name.
        """
        first_dir = Path("/")

        parts = Path(self.path).parts
        if len(parts) > 2:
            first_dir = Path("".join(parts[0:2]))

        return str(first_dir)

    @factory.lazy_attribute
    def directory(self):
        """
        Return file parent directory name from 'path' attribute value.

        Returns:
            string: Directory name.
        """
        return str(Path(self.path).parent.name)

    @factory.lazy_attribute
    def name(self):
        """
        Return name from 'path' attribute value.

        Returns:
            string: Filename.
        """
        return str(Path(self.path).name)

    @factory.lazy_attribute
    def extension(self):
        """
        Return file extension from 'path' attribute value.

        Returns:
            string: File extension without leading dot.
        """
        return str(Path(self.path).suffix)[1:]

    @factory.lazy_attribute
    def container(self):
        """
        Return container name deducted from 'extension' attribute.

        Returns:
            string: Media container name if extension exists in 'MEDIAS_CONTAINERS' else
            it will be the default container name 'MEDIAS_DEFAULT_CONTAINER_NAME' for
            unknow media type.
        """
        suffix = str(Path(self.path).suffix)[1:]
        if suffix not in MEDIAS_CONTAINERS:
            return MEDIAS_DEFAULT_CONTAINER_NAME

        return MEDIAS_CONTAINERS[suffix]

    @factory.lazy_attribute
    def mtime(self):
        """
        Return current date.

        Returns:
            string: Current time in ISO format.
        """
        # NOTE: Currently Deovi dump date are not timezone aware
        # return timezone.now().isoformat()
        return datetime.datetime.now()


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
