import datetime

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction
from django.utils import timezone

import pytest

from django_deovi.dump import DumpedFile
from django_deovi.models import Device, MediaFile


def test_mediafile_basic(db):
    """
    Basic model saving with required fields should not fail
    """
    device = Device(title="Foo", slug="foo")
    device.save()

    mediafile = MediaFile(
        device=device,
        path="/home/foo/bar/plop.mp4",
        absolute_dir="/home/foo/bar",
        filename="plop.mp4",
        dirname="bar",
        container="mp4",
        filesize=4096,
        stored_date=timezone.now(),
    )
    mediafile.full_clean()
    mediafile.save()

    assert 1 == MediaFile.objects.filter(path="/home/foo/bar/plop.mp4").count()
    assert "/home/foo/bar/plop.mp4" == mediafile.path


def test_mediafile_required_fields(db):
    """
    Basic model validation with missing required files should fail
    """
    mediafile = MediaFile()

    with pytest.raises(ValidationError) as excinfo:
        mediafile.full_clean()

    assert excinfo.value.message_dict == {
        "device": ["This field cannot be null."],
        "path": ["This field cannot be blank."],
        "absolute_dir": ["This field cannot be blank."],
        "filename": ["This field cannot be blank."],
        "container": ["This field cannot be blank."],
        "stored_date": ["This field cannot be null."],
    }


def test_mediafile_path_uniqueness(db):
    """
    MediaFile device + path uniqueness constraint should be respected.
    """
    device_foo = Device(title="Foo", slug="foo")
    device_foo.save()
    device_bar = Device(title="Bar", slug="bar")
    device_bar.save()

    dump_first = MediaFile(
        device=device_foo,
        path="/home/foo/bar/plop.mp4",
        absolute_dir="/home/foo/bar",
        filename="plop.mp4",
        dirname="bar",
        container="mp4",
        filesize=4096,
        stored_date=timezone.now(),
    )
    dump_first.save()

    dump_second = MediaFile(
        device=device_foo,
        path="/home/foo/bar/plop.mp4",
        absolute_dir="/home/foo/bar",
        filename="plop.mp4",
        dirname="bar",
        container="mp4",
        filesize=4096,
        stored_date=timezone.now(),
    )

    # Uniqueness constraint is respected, there can only be an unique path for the same
    # device
    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            dump_second.save()

        assert str(excinfo.value) == (
            "UNIQUE constraint failed: django_deovi_mediafile.device_id, "
            "django_deovi_mediafile.path"
        )

    # However a same path can exist on another device
    dump_third = MediaFile(
        device=device_bar,
        path="/home/foo/bar/plop.mp4",
        absolute_dir="/home/foo/bar",
        filename="plop.mp4",
        dirname="bar",
        container="mp4",
        filesize=4096,
        stored_date=timezone.now(),
    )
    dump_third.save()
