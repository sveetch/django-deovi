from pathlib import Path

from django_deovi.factories import DeviceFactory, DirectoryFactory


def test_directory_creation(db):
    """
    Factory should correctly create a new object without any errors
    """
    directory = DirectoryFactory(title="Directory 0")

    assert directory.title == "Directory 0"
    # Ensure it's dirpath, not a filepath (with a suffix)
    assert Path(directory.path).suffix == ""

    device = DeviceFactory()
    directory = DirectoryFactory(device=device, path="/home/foo")

    assert directory.path == "/home/foo"
    assert directory.device == device
