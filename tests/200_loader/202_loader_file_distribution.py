import logging

from django_deovi import __pkgname__
from django_deovi.models import MediaFile
from django_deovi.factories import (
    DirectoryFactory, DumpedFileFactory, MediaFileFactory
)
from django_deovi.loader import DumpLoader


def test_dumploader_file_distribution(db, caplog):
    """
    Given dumped files should be correctly distribued to edition and creation queue
    lists respectively whether if they already exist in database or not.
    """
    caplog.set_level(logging.DEBUG, logger=__pkgname__)

    directory = DirectoryFactory(path="/videos")

    loader = DumpLoader()

    # Create existing MediaFile objects
    MediaFileFactory(
        directory=directory,
        path="/videos/BillyBoy_S01E01.mkv",
        filesize=1105021329,
    )
    MediaFileFactory(
        directory=directory,
        path="/videos/BillyBoy_S01E02.mkv",
        filesize=777051908,
    )
    MediaFileFactory(
        directory=directory,
        path="/videos/BillyBoy_S01E03.mkv",
        filesize=906120796,
    )
    MediaFileFactory(
        directory=directory,
        path="/videos/BillyBoy_S02E01.mkv",
        filesize=1024,
    )

    # Create dump files
    dump_s01e01 = DumpedFileFactory(path="/videos/BillyBoy_S01E01.mkv")
    dump_s01e03 = DumpedFileFactory(path="/videos/BillyBoy_S01E03.mkv")
    dump_s01e04 = DumpedFileFactory(path="/videos/BillyBoy_S01E04.mkv")

    # Distribute a dump of not yet loaded files
    to_create, to_edit = loader.file_distribution(directory, [
        dump_s01e01.to_dict(),
        dump_s01e03.to_dict(),
        dump_s01e04.to_dict(),
    ])

    assert to_create == [dump_s01e04]
    assert to_edit == [dump_s01e01, dump_s01e03]

    assert caplog.record_tuples == [
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
    ]
