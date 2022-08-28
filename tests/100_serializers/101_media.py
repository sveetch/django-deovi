import datetime
import json

import pytz

from django.conf import settings

from django_deovi.factories import MediaFileFactory
from django_deovi.serializers import MediaFileSerializer


def test_mediafile_serialize_single(db):
    """
    Single object serialization.
    """
    default_tz = pytz.timezone(settings.TIME_ZONE)

    # Create mediafile
    plop = MediaFileFactory(
        path="/home/foo/bar/plop.mp4",
        filesize=42,
        stored_date=default_tz.localize(datetime.datetime(2012, 10, 15, 12, 00)),
        loaded_date=default_tz.localize(datetime.datetime(2020, 8, 23, 19, 00)),
    )

    # Serialize mediafile
    serializer = MediaFileSerializer(plop)

    print()
    print(json.dumps(serializer.data, indent=4))
    print()

    expected = {
        "id": plop.id,
        "device": 1,
        "title": "",
        "path": "/home/foo/bar/plop.mp4",
        "absolute_dir": "/home/foo/bar",
        "directory": "bar",
        "filename": "plop.mp4",
        "container": "mp4",
        "filesize": 42,
        "stored_date": "2012-10-15T12:00:00-05:00",
        "loaded_date": "2020-08-23T19:00:00-05:00"
    }

    assert expected == serializer.data


def test_mediafile_deserialize_json(db):
    """
    Python deserialization.
    """
    default_tz = pytz.timezone(settings.TIME_ZONE)

    data = {
        "path": "/home/foo/bar/plop.mp4",
        "absolute_dir": "/home/foo/bar",
        "directory": "bar",
        "filename": "plop.mp4",
        "container": "mp4",
        "filesize": 42,
        "stored_date": "2012-10-15T12:00:00-05:00",
    }

    # Deserialize Python dict payload
    serializer = MediaFileSerializer(data=data)
    is_valid = serializer.is_valid()

    print()
    print(serializer.errors)
    print()

    assert is_valid == True
