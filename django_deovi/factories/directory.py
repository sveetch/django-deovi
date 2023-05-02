import uuid
from pathlib import Path

import factory

from smart_media.utils.factories import create_image_file

from ..models import Directory
from .device import DeviceFactory


class DirectoryFactory(factory.django.DjangoModelFactory):
    """
    Factory to create instance of a Directory.
    """
    device = factory.SubFactory(DeviceFactory)
    title = factory.Sequence(lambda n: "Directory {0}".format(n))
    payload = "{}"

    class Meta:
        model = Directory

    class Params:
        filepath = factory.Faker("file_path", depth=3, category="video", absolute=True)

    @factory.lazy_attribute
    def checksum(self):
        """
        Return an UUID4

        Returns:
            string: Generated UUID4.
        """
        return uuid.uuid4()

    @factory.lazy_attribute
    def cover(self):
        """
        Fill file field with generated image.

        Returns:
            django.core.files.File: File object.
        """

        return create_image_file()

    @factory.lazy_attribute
    def path(self):
        """
        Return absolute directory from 'path' attribute value.

        Returns:
            string: Absolute directory path.
        """
        return str(Path(self.filepath).parent)
