import datetime

from django.utils import timezone

import pytest

from django_deovi.dump import DumpedFile
from django_deovi.exceptions import DjangoDeoviError


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


def test_dumpedfile_set_fields(db):
    """
    Errors should be raised for missing required arguments.
    """
    with pytest.raises(DjangoDeoviError) as excinfo:
        DumpedFile(path="/home/plop.mp4")

    assert str(excinfo.value) == (
        "DumpedFile missed some required arguments: name, absolute_dir, "
        "relative_dir, directory, extension, container, size, mtime"
    )


def test_dumpedfile_mtime_vaidation(db):
    """
    Error should be raised if mtime is not a string
    """
    with pytest.raises(DjangoDeoviError) as excinfo:
        DumpedFile(
            path="/home/foo/bar/plop.mp4",
            absolute_dir="/home/foo/bar",
            relative_dir="foo/bar",
            directory="bar",
            name="plop.mp4",
            extension="mp4",
            container="MP4",
            size=4096,
            mtime=42,
        )

    assert str(excinfo.value) == (
        "DumpedFile.mtime must be a string in ISO format."
    )
