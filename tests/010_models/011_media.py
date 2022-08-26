from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction
from django.utils import timezone

import pytest

from django_deovi.models import MediaFile


def test_basic(db):
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


def test_required_fields(db):
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


def test_path_uniqueness(db):
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
