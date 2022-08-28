import datetime

import pytest

from django.utils import timezone

from django_deovi.dump import DumpedFile
from django_deovi.factories import DumpedFileFactory


def test_dumpedfile_creation(db):
    """
    Factory should correctly create a new object without any errors
    """
    mediafile = DumpedFileFactory()

    assert mediafile.path.startswith("/") is True
    assert mediafile.path.endswith(mediafile.name) is True
    assert mediafile.path.endswith(mediafile.extension) is True
    assert mediafile.size > 0

    mediafile = DumpedFileFactory(path="/home/foo/plop.avi")

    #print()
    #print("mediafile.path:", mediafile.path)
    #print("mediafile.name:", mediafile.name)
    #print("mediafile.extension:", mediafile.extension)
    #print("mediafile.container:", mediafile.container)
    #print()

    assert mediafile.name == "plop.avi"
    assert mediafile.directory == "foo"
    assert mediafile.extension == "avi"

    # With a non hashable object, the Factory.build() method also return an object
    # instead of a dict
    mediafile = DumpedFileFactory(path="/home/bar/plip.mkv")

    assert isinstance(mediafile, DumpedFile) is True


def test_dumpedfile_to_dict(db):
    """
    Dump model object can be returned as dictionnary
    """
    mediafile = DumpedFileFactory(
        path="/home/foo/plop.mkv",
        size=42,
        mtime="2022-06-13T02:27:38",
    )

    assert mediafile.to_dict() == {
        "path": "/home/foo/plop.mkv",
        "name": "plop.mkv",
        "absolute_dir": "/home/foo",
        "relative_dir": "/home",
        "directory": "foo",
        "extension": "mkv",
        "container": "Matroska",
        "size": 42,
        "mtime": "2022-06-13T02:27:38",
    }


def test_dumpedfile_from_dict(db):
    """
    Dump model object can be created from given dictionnary
    """
    built = DumpedFileFactory(
        path="/home/foo/plop.mkv",
        size=42,
        mtime="2022-06-13T02:27:38",
    )

    mediafile = DumpedFile.from_dict(**built.to_dict())

    assert mediafile.to_dict() == {
        "path": "/home/foo/plop.mkv",
        "name": "plop.mkv",
        "absolute_dir": "/home/foo",
        "relative_dir": "/home",
        "directory": "foo",
        "extension": "mkv",
        "container": "Matroska",
        "size": 42,
        "mtime": "2022-06-13T02:27:38",
    }


def test_dumpedfile_convert_to_orm_fields(db):
    """
    Dump model object should be able to correctly convert its fields to the MediaFile
    model field names.
    """
    dummy_date = "2022-06-13T02:27:38"
    default_tz = timezone.get_default_timezone()
    localized_date = default_tz.localize(
        datetime.datetime.fromisoformat(dummy_date)
    )

    mediafile = DumpedFileFactory(
        path="/home/foo/plop.mkv",
        size=42,
        mtime=dummy_date,
    )

    assert mediafile.convert_to_orm_fields() == {
        "path": "/home/foo/plop.mkv",
        "filename": "plop.mkv",
        "absolute_dir": "/home/foo",
        "directory": "foo",
        "container": "mkv",
        "filesize": 42,
        "stored_date": localized_date,
    }
