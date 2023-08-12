import datetime

import pytest

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction
from django.utils import timezone

from django_deovi.models import Device
from django_deovi.factories import DeviceFactory, DirectoryFactory, MediaFileFactory


def test_device_basic(db):
    """
    Basic model saving with required fields should not fail
    """
    device = Device(title="Foo bar", slug="foo-bar")
    device.full_clean()
    device.save()

    assert 1 == Device.objects.count()


def test_device_required_fields(db):
    """
    Basic model validation with missing required files should fail
    """
    device = Device()

    with pytest.raises(ValidationError) as excinfo:
        device.full_clean()

    assert excinfo.value.message_dict == {
        "title": ["This field cannot be blank."],
        "slug": ["This field cannot be blank."],
    }


def test_device_path_uniqueness(db):
    """
    Device.path uniqueness constraint should be respected.
    """
    device_first = Device(
        title="Foo bar",
        slug="foo-bar",
    )
    device_first.save()

    device_bis = Device(
        title="Foo foo",
        slug="foo-bar",
    )

    # Uniqueness constraint is respected
    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            device_bis.save()

        assert str(excinfo.value) == (
            "UNIQUE constraint failed: django_deovi_device.slug"
        )


def test_device_resume(db):
    """
    Computed informations should be accurate.
    """
    current_tz = timezone.get_default_timezone()

    primary = DeviceFactory(slug="primary")
    secondary = DeviceFactory(slug="secondary")
    empty = DeviceFactory(slug="empty")

    goods = DirectoryFactory(device=primary, path="/videos/goods")
    bads = DirectoryFactory(device=primary, path="/videos/bads")
    nopes = DirectoryFactory(device=secondary, path="/videos/nopes")

    date_1_jan = datetime.datetime(2022, 1, 1).replace(tzinfo=current_tz)
    date_14_jul = datetime.datetime(2022, 7, 14).replace(tzinfo=current_tz)
    date_31_oct = datetime.datetime(2022, 10, 31).replace(tzinfo=current_tz)

    # Create some files for directories
    MediaFileFactory(directory=goods, filesize=128, loaded_date=date_14_jul)
    good_last = MediaFileFactory(directory=goods, filesize=128, loaded_date=date_31_oct)
    MediaFileFactory(directory=goods, filesize=256, loaded_date=date_1_jan)
    MediaFileFactory(directory=bads, filesize=100, loaded_date=date_1_jan)
    MediaFileFactory(directory=bads, filesize=11, loaded_date=date_14_jul)
    nope_last = MediaFileFactory(directory=nopes, filesize=555, loaded_date=date_1_jan)

    assert primary.resume() == {
        "directories": 2,
        "mediafiles": 5,
        "filesize": 623,
        "last_media_update": good_last.loaded_date,
    }

    assert secondary.resume() == {
        "directories": 1,
        "mediafiles": 1,
        "filesize": 555,
        "last_media_update": nope_last.loaded_date,
    }

    assert empty.resume() == {
        "directories": 0,
        "mediafiles": 0,
        "filesize": 0,
        "last_media_update": None,
    }


def test_device_get_directory_tree(db):
    """
    Method should recursively retrieves all device directories and output a tree as a
    nested dictionnary.
    """
    # Create device
    device = DeviceFactory(title="Master", slug="master")

    # Directories to fill with a mediafile
    filled_dirs = [
        DirectoryFactory(device=device, path="/home/a"),
        DirectoryFactory(device=device, path="/home/b"),
        DirectoryFactory(device=device, path="/home/a/aa/aaa"),
        DirectoryFactory(device=device, path="/home/b/bb"),
    ]
    # Additional empty dir between two filled dirs
    DirectoryFactory(device=device, path="/home/a/aa")

    # Empty directory without any file
    DirectoryFactory(device=device, path="/home/a/empty")

    # Fill directories
    for item in filled_dirs:
        path = "{base}/plop.avi".format(base=item)
        MediaFileFactory(directory=item, path=path, filesize=5)

    # Additional files only for last filled dir
    last_dir = filled_dirs[-1]
    path = "{base}/plip.avi".format(base=last_dir)
    MediaFileFactory(directory=last_dir, path=path, filesize=11)

    # Build tree
    result = device.get_directory_tree()

    # print()
    # print(json.dumps(result, indent=4))
    # print()

    assert result == {
        "name": "home",
        "filepath": "/home",
        "total_files": 0,
        "total_filesize": 0,
        "recursive_files": 5,
        "recursive_filesize": 31,
        "children": [
            {
                "name": "a",
                "filepath": "/home/a",
                "total_files": 1,
                "total_filesize": 5,
                "recursive_files": 2,
                "recursive_filesize": 10,
                "children": [
                    {
                        "name": "aa",
                        "filepath": "/home/a/aa",
                        "total_files": 0,
                        "total_filesize": 0,
                        "recursive_files": 1,
                        "recursive_filesize": 5,
                        "children": [
                            {
                                "name": "aaa",
                                "filepath": "/home/a/aa/aaa",
                                "total_files": 1,
                                "total_filesize": 5,
                                "recursive_files": 1,
                                "recursive_filesize": 5
                            }
                        ]
                    },
                    {
                        "name": "empty",
                        "filepath": "/home/a/empty",
                        "total_files": 0,
                        "total_filesize": 0,
                        "recursive_files": 0,
                        "recursive_filesize": 0
                    }
                ]
            },
            {
                "name": "b",
                "filepath": "/home/b",
                "total_files": 1,
                "total_filesize": 5,
                "recursive_files": 3,
                "recursive_filesize": 21,
                "children": [
                    {
                        "name": "bb",
                        "filepath": "/home/b/bb",
                        "total_files": 2,
                        "total_filesize": 16,
                        "recursive_files": 2,
                        "recursive_filesize": 16
                    }
                ]
            }
        ]
    }
