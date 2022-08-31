import datetime

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction
from django.utils import timezone

import pytest

from django_deovi.dump import DumpedFile
from django_deovi.models import Device, Directory, MediaFile


def test_mediafile_basic(db):
    """
    Basic model saving with required fields should not fail
    """
    device = Device(title="Foo bar", slug="foo-bar")
    device.save()

    directory = Directory(device=device, title="Foo", path="/home/foo/bar")
    directory.save()

    mediafile = MediaFile(
        directory=directory,
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
        "directory": ["This field cannot be null."],
        "path": ["This field cannot be blank."],
        "absolute_dir": ["This field cannot be blank."],
        "filename": ["This field cannot be blank."],
        "container": ["This field cannot be blank."],
        "stored_date": ["This field cannot be null."],
    }


def test_mediafile_path_uniqueness(db):
    """
    MediaFile directory + path uniqueness constraint should be respected.
    """
    device = Device(title="Foo bar", slug="foo-bar")
    device.save()

    directory_foo = Directory(device=device, title="Foo", path="/home/foo")
    directory_foo.save()

    dump_first = MediaFile(
        directory=directory_foo,
        path="/home/foo/plop.mp4",
        absolute_dir="/home/foo",
        filename="plop.mp4",
        dirname="bar",
        container="mp4",
        filesize=4096,
        stored_date=timezone.now(),
    )
    dump_first.save()

    dump_second = MediaFile(
        directory=directory_foo,
        path="/home/foo/plop.mp4",
        absolute_dir="/home/foo",
        filename="plop.mp4",
        dirname="bar",
        container="mp4",
        filesize=4096,
        stored_date=timezone.now(),
    )

    # Uniqueness constraint is respected, there can only be an unique path for the same
    # directory
    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            dump_second.save()

        assert str(excinfo.value) == (
            "UNIQUE constraint failed: django_deovi_mediafile.directory_id, "
            "django_deovi_mediafile.path"
        )

    # However a same path can exist on another directory
    directory_bar = Directory(device=device, title="Bar", path="/home/foo/bar")
    directory_bar.save()

    dump_third = MediaFile(
        directory=directory_bar,
        path="/home/foo/bar/plop.mp4",
        absolute_dir="/home/foo/bar",
        filename="plop.mp4",
        dirname="bar",
        container="mp4",
        filesize=4096,
        stored_date=timezone.now(),
    )
    dump_third.save()
