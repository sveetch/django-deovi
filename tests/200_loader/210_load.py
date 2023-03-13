import logging
import json

from django_deovi import __pkgname__
from django_deovi.models import MediaFile
from django_deovi.factories import (
    DeviceFactory, DirectoryFactory, MediaFileFactory
)
from django_deovi.loader import DumpLoader


def test_dumploader_load(db, caplog, tests_settings):
    """
    Loader should correctly load directories and files from given dump.
    """
    caplog.set_level(logging.DEBUG, logger=__pkgname__)

    # Simplify dump to only keep a single directory
    dump_path = tests_settings.fixtures_path / "dump_directories.json"
    dump_content = {
        "series/BillyBoy": json.loads(dump_path.read_text())["series/BillyBoy"]
    }

    device = DeviceFactory(slug="donald")
    directory = DirectoryFactory(
        device=device,
        path="/videos/series/BillyBoy"
    )

    # Create existing MediaFile objects
    BillyBoy_S01E01 = MediaFileFactory(
        path="/videos/series/BillyBoy/BillyBoy_S01E01.mkv",
        directory=directory,
        filesize=100,
    )

    # Proceed to loading
    loader = DumpLoader()
    loader.load(device.slug, dump_content)

    assert MediaFile.objects.count() == 3

    # Ensure each difference have been applied and nothing have been dropped
    fetched_s01e01 = MediaFile.objects.get(path=BillyBoy_S01E01.path)
    assert fetched_s01e01.filesize == 101

    assert caplog.record_tuples == [
        (
            __pkgname__,
            logging.INFO,
            "🏷️Using device slug: donald"
        ),
        (
            __pkgname__,
            logging.DEBUG,
            "- Got an existing device for given slug"
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
            "- Found 1 existing MediaFile objects related to this dump"
        ),
        (
            __pkgname__,
            logging.INFO,
            "- Files entry to create: 2"
        ),
        (
            __pkgname__,
            logging.INFO,
            "- Files entry to edit: 1"
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
    ]


def test_dumploader_load_new_device_no_dirs(db, caplog, tests_settings):
    """
    Check loader behavior with not existing yet device and an empty fake dump,
    everything should goes well without error.
    """
    caplog.set_level(logging.DEBUG, logger=__pkgname__)

    # Proceed to loading
    loader = DumpLoader()
    loader.load("nope", {})

    assert MediaFile.objects.count() == 0

    assert caplog.record_tuples == [
        (
            __pkgname__,
            logging.INFO,
            "🏷️Using device slug: nope"
        ),
        (
            __pkgname__,
            logging.DEBUG,
            "- New device created for given slug"
        ),
    ]
