import datetime

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction
from django.utils import timezone

import pytest

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
    bad_last = MediaFileFactory(directory=bads, filesize=11, loaded_date=date_14_jul)
    nope_last = MediaFileFactory(directory=nopes, filesize=555, loaded_date=date_1_jan)

    assert primary.resume() == {
        "directories": 2,
        "mediafiles": 5,
        "filesize": 623,
        "last_update": good_last.loaded_date,
    }

    assert secondary.resume() == {
        "directories": 1,
        "mediafiles": 1,
        "filesize": 555,
        "last_update": nope_last.loaded_date,
    }

    assert empty.resume() == {
        "directories": 0,
        "mediafiles": 0,
        "filesize": 0,
        "last_update": None,
    }
