import factory

from ..models import Device


class DeviceFactory(factory.django.DjangoModelFactory):
    """
    Factory to create instance of a Device.
    """
    title = factory.Sequence(lambda n: "Device {0}".format(n))
    slug = factory.Sequence(lambda n: "device-{0}".format(n))

    class Meta:
        model = Device
