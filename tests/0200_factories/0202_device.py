from django_deovi.factories import DeviceFactory


def test_device_creation(db):
    """
    Factory should correctly create a new object without any errors
    """
    device = DeviceFactory(slug="device-0")

    assert device.slug == "device-0"

    device = DeviceFactory(title="Plop", slug="plip")

    assert device.slug == "plip"
