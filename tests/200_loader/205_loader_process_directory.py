import logging
from pathlib import Path

import pytest

from django_deovi import __pkgname__
from django_deovi.models import Directory, MediaFile
from django_deovi.factories import (
    DeviceFactory, DirectoryFactory, MediaFileFactory
)
from django_deovi.loader import DumpLoader
from django_deovi.utils.tests import sum_file_object


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
def test_loader_is_directory_elligible(from_checksum, to_checksum, created,
                                           expected):
    """
    Method should correctly check if directory has change to be done.
    """
    loader = DumpLoader()

    assert loader._is_directory_elligible(
        from_checksum, to_checksum, created
    ) is expected


def test_loader_get_attached_file(db, caplog, tests_settings):
    """
    Method should be able to resolve path and return a proper Django File object.
    """
    basepath = tests_settings.fixtures_path / "covers"

    loader = DumpLoader()

    # Given path does not exists
    result = loader.get_attached_file(Path("nope.png"), basepath=basepath)
    assert result is None

    result = loader.get_attached_file(Path("blue.png"))
    assert result is None

    # Relative path to the given basepath
    result = loader.get_attached_file(Path("blue.png"), basepath=basepath)
    assert result.name == basepath / Path("blue.png")

    # The same with a string path instead of Path object
    result = loader.get_attached_file("blue.png", basepath=basepath)
    assert result.name == basepath / Path("blue.png")

    # Relative path starting with a dir
    result = loader.get_attached_file(
        Path("covers/blue.png"),
        basepath=tests_settings.fixtures_path
    )
    assert result.name == basepath / Path("blue.png")

    # With absolute path, basepath argument is ignored
    result = loader.get_attached_file(basepath / Path("blue.png"))
    assert result.name == basepath / Path("blue.png")

    result = loader.get_attached_file(basepath / Path("blue.png"), basepath=basepath)
    assert result.name == basepath / Path("blue.png")


def test_loader_process_directory_basic(db, caplog, tests_settings):
    """
    Loader should process directories with their files and log some infos
    """
    caplog.set_level(logging.DEBUG, logger=__pkgname__)

    device = DeviceFactory()
    billyserie_dir = DirectoryFactory(
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
        directory=billyserie_dir,
        filesize=100,
    )
    BillyBoy_S01E03 = MediaFileFactory(
        path="/videos/series/BillyBoy/BillyBoy_S01E03.mkv",
        directory=billyserie_dir,
        filesize=300,
    )
    BillyBoy_S02E01 = MediaFileFactory(
        path="/videos/series/BillyBoy/BillyBoy_S02E01.mkv",
        directory=billyserie_dir,
    )
    Coucou_1982 = MediaFileFactory(
        path="/videos/theatre/Coucou_1982.avi",
        directory=theatre_dir,
        filesize=1982,
    )

    dump_path = tests_settings.fixtures_path / "dump_directories.json"

    loader = DumpLoader()
    dump_content = loader.open_dump(dump_path)
    loader.process_directory(device, dump_content, tests_settings.fixtures_path)

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


def test_loader_process_directory_checksum(db, caplog, tests_settings):
    """
    Checksum behaviors should be properly implemented to update object only if
    it have different checksum or if it's a new directory.
    """
    caplog.set_level(logging.DEBUG, logger=__pkgname__)

    dump_path = tests_settings.fixtures_path / "dump_directories.json"
    covers_basepath = tests_settings.fixtures_path / "covers"

    device = DeviceFactory()

    # Create existing Directory objects
    billyserie_dir = DirectoryFactory(
        device=device,
        path="/videos/series/BillyBoy",
        checksum="001",
    )
    theatre_dir = DirectoryFactory(
        device=device,
        path="/videos/theatre",
        checksum="010",
    )

    # Create existing MediaFile objects
    BillyBoy_S01E01 = MediaFileFactory(
        path="/videos/series/BillyBoy/BillyBoy_S01E01.mkv",
        directory=billyserie_dir,
        filesize=100,
    )
    Coucou_1982 = MediaFileFactory(
        path="/videos/theatre/Coucou_1982.avi",
        directory=theatre_dir,
        filesize=1982,
    )

    # Open sample dump
    loader = DumpLoader()
    dump_content = loader.open_dump(dump_path)

    # Patch dump to fill some fields that fixture file does not include
    # Identical checksum discard any update
    dump_content["series/BillyBoy"]["checksum"] = "001"
    # Different checksum let file distribution process
    dump_content["theatre"]["checksum"] = "011"

    # Patch titles
    dump_content["theatre"]["title"] = "Theater"
    dump_content["series/ZouipWorld"]["title"] = "Zouippy"
    # Patch title but it won't be applied since 'billyserie_dir' checksum has not
    # changed (this should not happen in real usage but check it just to be sure)
    dump_content["series/BillyBoy"]["title"] = "foobar"

    # Give a new cover filepath to every directory
    dump_content["series/BillyBoy"]["cover"] = "covers/blue.png"
    dump_content["theatre"]["cover"] = "covers/red.png"
    dump_content["series/ZouipWorld"]["cover"] = "covers/yellow.png"

    # Process patched dump
    saved = loader.process_directory(
        device,
        dump_content,
        tests_settings.fixtures_path,
    )
    results = [
        (directory.path, created)
        for directory, created in saved
    ]
    assert results == [
        ("/videos/series/ZouipWorld", True),
        ("/videos/theatre", False)
    ]

    assert MediaFile.objects.count() == 3

    # Get directory objects from db
    billyserie_instance = Directory.objects.get(path="/videos/series/BillyBoy")
    theatre_instance = Directory.objects.get(path="/videos/theatre")
    zouipworld_instance = Directory.objects.get(path="/videos/series/ZouipWorld")

    # Original checksum is still there
    assert billyserie_instance.checksum == "001"
    # Checksum have been saved
    assert theatre_instance.checksum == "011"
    # New object did not have any checksum but a new one have been generated
    assert zouipworld_instance.checksum is not None

    # Title did not change
    assert billyserie_instance.title == billyserie_dir.title
    # Objects with new checksum trigger save and adopt changes
    assert theatre_instance.title == "Theater"
    assert zouipworld_instance.title == "Zouippy"

    # Cover did not change because of identical checksum
    with (covers_basepath / "blue.png").open(mode="rb") as fp:
        assert sum_file_object(billyserie_instance.cover.file) != sum_file_object(fp)

    # Cover has been correctly updated
    with (covers_basepath / "red.png").open(mode="rb") as fp:
        assert sum_file_object(theatre_instance.cover.file) == sum_file_object(fp)

    with (covers_basepath / "yellow.png").open(mode="rb") as fp:
        assert sum_file_object(zouipworld_instance.cover.file) == sum_file_object(fp)
