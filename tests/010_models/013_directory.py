import json
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


def test_directory_payload(db):
    """
    Given payload should be validated to be a valid JSON Object.
    """
    device = Device(title="Foo bar", slug="foo-bar")
    device.save()

    # Not JSON valid format
    directory = Directory(
        device=device,
        title="Foo bar",
        path="/foo/bar",
        payload="niet",
    )

    with pytest.raises(ValidationError) as excinfo:
        directory.full_clean()

    assert excinfo.value.message_dict == {
        "payload": ["Given payload is not a valid JSON format."],
    }

    # Not JSON Object
    directory = Directory(
        device=device,
        title="Foo bar",
        path="/foo/bar",
        payload="[]",
    )

    with pytest.raises(ValidationError) as excinfo:
        directory.full_clean()

    assert excinfo.value.message_dict == {
        "payload": ["Given payload is not a valid JSON Object."],
    }

    # Valid JSON Object
    directory = Directory(
        device=device,
        title="Foo bar",
        path="/foo/bar",
        payload='{"foo": "bar"}',
    )
    directory.full_clean()
    directory.save()

    assert directory.get_payload_object() == {"foo": "bar"}


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


def test_directory_resume(db):
    """
    Computed informations should be accurate.
    """
    current_tz = timezone.get_default_timezone()

    device = DeviceFactory()

    kiwis = DirectoryFactory(device=device, path="/videos/kiwis", payload=json.dumps({
        "meep": "meep",
        "plip": "plop",
    }))
    apples = DirectoryFactory(device=device, path="/videos/apples", payload=json.dumps({
        "plip": "plop",
        "filesize": "niet",
    }))
    bananas = DirectoryFactory(device=device, path="/videos/bananas")

    date_1_jan = datetime.datetime(2022, 1, 1).replace(tzinfo=current_tz)
    date_14_jul = datetime.datetime(2022, 7, 14).replace(tzinfo=current_tz)
    date_31_oct = datetime.datetime(2022, 10, 31).replace(tzinfo=current_tz)

    # Create some files for directories
    MediaFileFactory(directory=kiwis, filesize=128, loaded_date=date_14_jul)
    kiwi_last = MediaFileFactory(directory=kiwis, filesize=128, loaded_date=date_31_oct)
    MediaFileFactory(directory=kiwis, filesize=256, loaded_date=date_1_jan)
    MediaFileFactory(directory=apples, filesize=100, loaded_date=date_1_jan)
    apple_last = MediaFileFactory(directory=apples, filesize=11, loaded_date=date_14_jul)
    banana_last = MediaFileFactory(directory=bananas, filesize=555, loaded_date=date_1_jan)

    assert kiwis.resume() == {
        "mediafiles": 3,
        "filesize": 512,
        "last_media_update": kiwi_last.loaded_date,
        "meep": "meep",
        "plip": "plop",
    }

    assert apples.resume() == {
        "mediafiles": 2,
        "filesize": 111,
        "last_media_update": apple_last.loaded_date,
        "plip": "plop",
    }

    assert bananas.resume() == {
        "mediafiles": 1,
        "filesize": 555,
        "last_media_update": banana_last.loaded_date,
    }
