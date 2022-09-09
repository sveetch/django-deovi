import datetime

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction
from django.utils import timezone

import pytest

from django_deovi.models import Device
from django_deovi.models import Directory
from django_deovi.factories import DeviceFactory, DirectoryFactory, MediaFileFactory


def test_directory_basic(db):
    """
    Basic model saving with required fields should not fail
    """
    device = Device(title="Foo bar", slug="foo-bar")
    device.save()

    directory = Directory(
        device=device,
        title="Foo bar",
        path="/foo/bar",
    )
    directory.full_clean()
    directory.save()

    assert 1 == Directory.objects.count()


def test_directory_required_fields(db):
    """
    Basic model validation with missing required files should fail
    """
    directory = Directory()

    with pytest.raises(ValidationError) as excinfo:
        directory.full_clean()

    assert excinfo.value.message_dict == {
        "device": ["This field cannot be null."],
        "path": ["This field cannot be blank."],
    }


def test_directory_path_uniqueness(db):
    """
    Directory.path uniqueness constraint should be respected.
    """
    device = Device(title="Foo bar", slug="foo-bar")
    device.save()

    directory_first = Directory(
        device=device,
        title="Foo bar",
        path="/foo/bar",
    )
    directory_first.save()

    directory_bis = Directory(
        device=device,
        title="Foo foo",
        path="/foo/bar",
    )

    # Uniqueness constraint is respected
    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            directory_bis.save()

        assert str(excinfo.value) == (
            "UNIQUE constraint failed: django_deovi_directory.device_id, "
            "django_deovi_directory.path"
        )


def test_device_resume(db):
    """
    Computed informations should be accurate.
    """
    current_tz = timezone.get_default_timezone()

    device = DeviceFactory()

    goods = DirectoryFactory(device=device, path="/videos/goods")
    bads = DirectoryFactory(device=device, path="/videos/bads")
    nopes = DirectoryFactory(device=device, path="/videos/nopes")

    date_1_jan = datetime.datetime(2022, 1, 1).replace(tzinfo=current_tz)
    date_14_jul = datetime.datetime(2022, 7, 14).replace(tzinfo=current_tz)
    date_31_oct = datetime.datetime(2022, 10, 31).replace(tzinfo=current_tz)

    # Create some files for directories
    MediaFileFactory(directory=goods, filesize=128, loaded_date=date_14_jul)
    good_last = MediaFileFactory(directory=goods, filesize=128, loaded_date=date_31_oct)
    MediaFileFactory(directory=goods, filesize=256, loaded_date=date_1_jan)
    MediaFileFactory(directory=bads, filesize=100, loaded_date=date_1_jan)
    bad_last = MediaFileFactory(directory=bads, filesize=11, loaded_date=date_14_jul)
    nope_last = MediaFileFactory(directory=nopes, filesize=555, loaded_date=date_1_jan)

    assert goods.resume() == {
        "mediafiles": 3,
        "filesize": 512,
        "last_update": good_last.loaded_date,
    }

    assert bads.resume() == {
        "mediafiles": 2,
        "filesize": 111,
        "last_update": bad_last.loaded_date,
    }

    assert nopes.resume() == {
        "mediafiles": 1,
        "filesize": 555,
        "last_update": nope_last.loaded_date,
    }
