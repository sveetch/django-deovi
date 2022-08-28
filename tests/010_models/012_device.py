import datetime

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction
from django.utils import timezone

import pytest

from django_deovi.models import Device


def test_device_basic(db):
    """
    Basic model saving with required fields should not fail
    """
    device = Device(
        title="Foo bar",
        slug="foo-bar",
    )
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
