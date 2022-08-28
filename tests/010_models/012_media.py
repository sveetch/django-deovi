import datetime

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction
from django.utils import timezone

import pytest

from django_deovi.dump import DumpedFile
from django_deovi.models import MediaFile


def test_mediafile_basic(db):
    """
    Basic model saving with required fields should not fail
    """
    mediafile = MediaFile(
        path="/home/foo/bar/plop.mp4",
        absolute_dir="/home/foo/bar",
        filename="plop.mp4",
        directory="bar",
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
        "path": ["This field cannot be blank."],
        "absolute_dir": ["This field cannot be blank."],
        "filename": ["This field cannot be blank."],
        "container": ["This field cannot be blank."],
        "stored_date": ["This field cannot be null."],
    }


def test_mediafile_path_uniqueness(db):
    """
    MediaFile.path uniqueness constraint should be respected.
    """
    dump_first = MediaFile(
        path="/home/foo/bar/plop.mp4",
        absolute_dir="/home/foo/bar",
        filename="plop.mp4",
        directory="bar",
        container="mp4",
        filesize=4096,
        stored_date=timezone.now(),
    )
    dump_first.save()

    dump_bis = MediaFile(
        path="/home/foo/bar/plop.mp4",
        absolute_dir="/home/foo/bar",
        filename="plop.mp4",
        directory="bar",
        container="mp4",
        filesize=4096,
        stored_date=timezone.now(),
    )

    # Uniqueness constraint is respected
    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            dump_bis.save()

        assert str(excinfo.value) == (
            "UNIQUE constraint failed: django_deovi_mediafile.path"
        )


def test_dumpedfile_basic(db):
    """
    Basic model creation with required fields should not fail
    """
    default_tz = timezone.get_default_timezone()

    mediafile = DumpedFile(
        path="/home/foo/bar/plop.mp4",
        absolute_dir="/home/foo/bar",
        relative_dir="foo/bar",
        directory="bar",
        name="plop.mp4",
        extension="mp4",
        container="MP4",
        size=4096,
        mtime="2022-08-11T12:00:35",
    )

    expected_stored_date = default_tz.localize(
        datetime.datetime(2022, 8, 11, 12, 00, 35)
    )

    assert repr(mediafile) == "<DumpedFile: /home/foo/bar/plop.mp4>"

    assert mediafile.to_dict() == {
        "path": "/home/foo/bar/plop.mp4",
        "absolute_dir": "/home/foo/bar",
        "relative_dir": "foo/bar",
        "directory": "bar",
        "name": "plop.mp4",
        "extension": "mp4",
        "container": "MP4",
        "size": 4096,
        "mtime": "2022-08-11T12:00:35",
    }

    assert mediafile.convert_to_orm_fields() == {
        "path": "/home/foo/bar/plop.mp4",
        "absolute_dir": "/home/foo/bar",
        "directory": "bar",
        "filename": "plop.mp4",
        "container": "mp4",
        "filesize": 4096,
        "stored_date": expected_stored_date,
    }
