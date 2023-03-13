import logging

import pytest

from django_deovi import __pkgname__
from django_deovi.models import MediaFile
from django_deovi.factories import (
    DeviceFactory, DirectoryFactory, MediaFileFactory
)
from django_deovi.loader import DumpLoader


@pytest.mark.parametrize("from_checksum, to_checksum, created, expected", [
    # Whatever checksum if item is created, it must be elligible
    (None, "foo", True, True),
    ("foo", None, True, True),
    ("foo", "foo", True, True),
    ("foo", "bar", True, True),
    # Once item is not created (edited), if checksum differ, item is elligible
    (None, "foo", False, True),
    ("foo", None, False, True),
    ("foo", "foo", False, False),
    ("foo", "bar", False, True),
])
def test_dumploader_is_directory_elligible(from_checksum, to_checksum, created,
                                           expected):
    """
    Method should correctly check if directory has change to be done.
    """
    loader = DumpLoader()

    assert loader._is_directory_elligible(
        from_checksum, to_checksum, created
    ) is expected


def test_dumploader_process_directory(db, caplog, tests_settings):
    """
    Dump should process directories and their files
    """
    caplog.set_level(logging.DEBUG, logger=__pkgname__)

    device = DeviceFactory()
    series_dir = DirectoryFactory(
        device=device,
        path="/videos/series/BillyBoy"
    )
    theatre_dir = DirectoryFactory(
        device=device,
        path="/videos/theatre"
    )

    # Create existing MediaFile objects
    BillyBoy_S01E01 = MediaFileFactory(
        path="/videos/series/BillyBoy/BillyBoy_S01E01.mkv",
        directory=series_dir,
        filesize=100,
    )
    BillyBoy_S01E03 = MediaFileFactory(
        path="/videos/series/BillyBoy/BillyBoy_S01E03.mkv",
        directory=series_dir,
        filesize=300,
    )
    BillyBoy_S02E01 = MediaFileFactory(
        path="/videos/series/BillyBoy/BillyBoy_S02E01.mkv",
        directory=series_dir,
    )
    Coucou_1982 = MediaFileFactory(
        path="/videos/theatre/Coucou_1982.avi",
        directory=theatre_dir,
        filesize=1982,
    )

    dump_path = tests_settings.fixtures_path / "dump_directories.json"

    loader = DumpLoader()
    dump_content = loader.open_dump(dump_path)
    loader.process_directory(device, dump_content)

    assert MediaFile.objects.count() == 6

    # Ensure each difference have been applied and nothing has been dropped
    fetched_s01e01 = MediaFile.objects.get(path=BillyBoy_S01E01.path)
    assert fetched_s01e01.filesize == 101

    fetched_s01e03 = MediaFile.objects.get(path=BillyBoy_S01E03.path)
    assert fetched_s01e03.filesize == 301

    fetched_coucou = MediaFile.objects.get(path=Coucou_1982.path)
    assert fetched_coucou.filesize == 2982

    assert caplog.record_tuples == [
        (
            __pkgname__,
            logging.INFO,
            "📂 Working on directory: /videos/series/ZouipWorld"
        ),
        (
            __pkgname__,
            logging.DEBUG,
            "- New directory created"
        ),
        (
            __pkgname__,
            logging.INFO,
            "- Files entry to create: 1"
        ),
        (
            __pkgname__,
            logging.DEBUG,
            "- Proceed to bulk creation"
        ),
        (
            __pkgname__,
            logging.INFO,
            "📂 Working on directory: /videos/series/BillyBoy"
        ),
        (
            __pkgname__,
            logging.DEBUG,
            "- Got an existing directory"
        ),
        (
            __pkgname__,
            logging.INFO,
            "- Found 2 existing MediaFile objects related to this dump"
        ),
        (
            __pkgname__,
            logging.INFO,
            "- Files entry to create: 1"
        ),
        (
            __pkgname__,
            logging.INFO,
            "- Files entry to edit: 2"
        ),
        (
            __pkgname__,
            logging.DEBUG,
            "- Proceed to bulk creation"
        ),
        (
            __pkgname__,
            logging.DEBUG,
            "- Proceed to bulk edition"
        ),
        (
            __pkgname__,
            logging.INFO,
            "📂 Working on directory: /videos/theatre"
        ),
        (
            __pkgname__,
            logging.DEBUG,
            "- Got an existing directory"
        ),
        (
            __pkgname__,
            logging.INFO,
            "- Found 1 existing MediaFile objects related to this dump"
        ),
        (
            __pkgname__,
            logging.INFO,
            "- Files entry to edit: 1"
        ),
        (
            __pkgname__,
            logging.DEBUG,
            "- Proceed to bulk edition"
        )
    ]


def test_dumploader_process_directory_checksum(db, caplog, tests_settings):
    """
    TODO
    """
    caplog.set_level(logging.DEBUG, logger=__pkgname__)

    device = DeviceFactory()
    series_dir = DirectoryFactory(
        device=device,
        path="/videos/series/BillyBoy",
        checksum="billy1",
    )
    theatre_dir = DirectoryFactory(
        device=device,
        path="/videos/theatre",
        checksum="theatre1",
    )

    # Create existing MediaFile objects
    BillyBoy_S01E01 = MediaFileFactory(
        path="/videos/series/BillyBoy/BillyBoy_S01E01.mkv",
        directory=series_dir,
        filesize=100,
    )
    Coucou_1982 = MediaFileFactory(
        path="/videos/theatre/Coucou_1982.avi",
        directory=theatre_dir,
        filesize=1982,
    )

    dump_path = tests_settings.fixtures_path / "dump_directories.json"

    loader = DumpLoader()
    dump_content = loader.open_dump(dump_path)

    # Identical checksum discard any update
    dump_content["series/BillyBoy"]["checksum"] = "billy1"
    # Different checksum let file distribution process
    dump_content["theatre"]["checksum"] = "theatre2"
    # When dir source or dump have no checksum, trigger the file distribution process
    dump_content["series/ZouipWorld"]["checksum"] = "zouipworld2"

    saved = loader.process_directory(device, dump_content)
    results = [
        (directory.path, created)
        for directory, created in saved
    ]

    assert results == [
        ("/videos/series/ZouipWorld", True),
        ("/videos/theatre", False)
    ]

    assert MediaFile.objects.count() == 3
