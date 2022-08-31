import datetime

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction
from django.utils import timezone

import pytest

from django_deovi.models import Device
from django_deovi.models import Directory


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
