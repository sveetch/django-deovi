from pathlib import Path

import factory

from ..models import Directory
from .device import DeviceFactory


class DirectoryFactory(factory.django.DjangoModelFactory):
    """
    Factory to create instance of a Directory.

    TODO: Implement the new fields.
    """
    device = factory.SubFactory(DeviceFactory)
    title = factory.Sequence(lambda n: "Directory {0}".format(n))

    class Meta:
        model = Directory

    class Params:
        filepath = factory.Faker("file_path", depth=3, category="video", absolute=True)

    @factory.lazy_attribute
    def path(self):
        """
        Return absolute directory from 'path' attribute value.

        Returns:
            string: Absolute directory path.
        """
        return str(Path(self.filepath).parent)
