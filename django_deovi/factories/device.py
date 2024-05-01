import factory

from ..models import Device


class DeviceFactory(factory.django.DjangoModelFactory):
    """
    Factory to create instance of a Device.
    """
    title = factory.Sequence(lambda n: "Device {0}".format(n))
    slug = factory.Sequence(lambda n: "device-{0}".format(n))
    disk_total = 0
    disk_used = 0
    disk_free = 0

    class Meta:
        model = Device
