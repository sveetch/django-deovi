import datetime
import logging
import json

import pytest

from django.db.utils import IntegrityError
from django.db import transaction
from django.utils import timezone

from django_deovi import __pkgname__
from django_deovi.models import MediaFile
from django_deovi.factories import (
    DeviceFactory, DirectoryFactory, DumpedFileFactory, MediaFileFactory
)
from django_deovi.loader import DumpLoader


def test_dumploader_get_existing(db, caplog):
    """
    Method should return every MediaFile corresponding to the given couple
    device + path.
    """
    caplog.set_level(logging.DEBUG, logger=__pkgname__)

    device = DeviceFactory()
    goods = DirectoryFactory(
        device=device,
        path="/videos/goods"
    )
    bads = DirectoryFactory(
        device=device,
        path="/videos/bads"
    )

    loader = DumpLoader()

    # Videos which will be found as existing
    picsou = MediaFileFactory(directory=goods, path="/videos/goods/picsou.mkv")
    donald = MediaFileFactory(directory=goods, path="/videos/goods/donald.mkv")
    daisy = MediaFileFactory(directory=goods, path="/videos/goods/daisy.mkv")
    # Some other videos for filling
    MediaFileFactory(directory=goods, path="/videos/goods/popop.mkv")
    MediaFileFactory(directory=bads, path="/videos/bads/miss-Tick.mkv")
    MediaFileFactory(directory=bads, path="/videos/bads/gripsou.mkv")

    existing = loader.get_existing(goods, [
        {"path": "/videos/goods/picsou.mkv"},
        {"path": "/videos/goods/donald.mkv"},
        {"path": "/videos/goods/daisy.mkv"},
        {"path": "/videos/goods/gontran.mkv"},
        {"path": "/home/donald.mkv"},
    ])

    assert existing == {
        picsou.path: picsou,
        donald.path: donald,
        daisy.path: daisy,
    }


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


def test_dumploader_create_files(db):
    """
    File to create should be correctly created in bulk from given data.
    """
    now = timezone.now()
    yesterday = now - datetime.timedelta(days=1)

    directory = DirectoryFactory(path="/videos")

    loader = DumpLoader()

    # Create dump files
    BillyBoy_S01E01 = DumpedFileFactory(path="/videos/BillyBoy_S01E01.mkv")
    BillyBoy_S01E03 = DumpedFileFactory(path="/videos/BillyBoy_S01E03.mkv")
    BillyBoy_S01E04 = DumpedFileFactory(path="/videos/BillyBoy_S01E04.mkv")

    # Distribute a dump of not yet loaded files
    loader.create_files(directory, [
        BillyBoy_S01E01,
        BillyBoy_S01E03,
        BillyBoy_S01E04,
    ], batch_date=yesterday)

    assert MediaFile.objects.count() == 3
    assert MediaFile.objects.filter(loaded_date=yesterday).count() == 3


def test_dumploader_create_uniqueness_path(db):
    """
    MediaFile directory + path uniqueness constraint should make the bulk chain to fail.
    """
    now = timezone.now()

    directory = DirectoryFactory(path="/videos")

    loader = DumpLoader()

    # Create the dumps to pass to bulk chain
    dump_first = DumpedFileFactory(path="/videos/foo_1.mkv")
    dump_second = DumpedFileFactory(path="/videos/foo_2.mkv")
    dump_third = DumpedFileFactory(path="/videos/foo_2.mkv")

    # Create the first dump file as an existing MediaFile object
    media_first = MediaFileFactory(
        directory=directory,
        **dump_first.convert_to_orm_fields()
    )

    # Against existing objects
    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            loader.create_files(directory, [
                dump_first,
                dump_second,
            ], batch_date=now)

        assert str(excinfo.value) == (
            "UNIQUE constraint failed: django_deovi_mediafile.directory_id, "
            "django_deovi_mediafile.path"
        )

    # The transaction don't let pass anything that was in the failed chain, there is
    # only the previously existing object
    assert MediaFile.objects.count() == 1

    # Against identical couple inside the bulk chain
    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            loader.create_files(directory, [
                dump_third,
                dump_third,
            ], batch_date=now)

        assert str(excinfo.value) == (
            "UNIQUE constraint failed: django_deovi_mediafile.directory_id, "
            "django_deovi_mediafile.path"
        )

    # The transaction don't let pass anything that was in the failed chain, there is
    # only the previously existing object
    assert MediaFile.objects.count() == 1


def test_dumploader_batch_limit(db):
    """
    The bulk limit should be respected if given and will create all items anyway.
    """
    now = timezone.now()

    directory = DirectoryFactory(path="/videos")

    loader = DumpLoader(batch_limit=2)

    # Create dump files
    BillyBoy_S01E01 = DumpedFileFactory(path="/videos/BillyBoy_S01E01.mkv")
    BillyBoy_S01E02 = DumpedFileFactory(path="/videos/BillyBoy_S01E02.mkv")
    BillyBoy_S01E03 = DumpedFileFactory(path="/videos/BillyBoy_S01E03.mkv")
    BillyBoy_S01E04 = DumpedFileFactory(path="/videos/BillyBoy_S01E04.mkv")

    # Distribute a dump of not yet loaded files
    loader.create_files(directory, [
        BillyBoy_S01E01,
        BillyBoy_S01E02,
        BillyBoy_S01E03,
        BillyBoy_S01E04,
    ], batch_date=now)

    assert MediaFile.objects.count() == 4


def test_dumploader_edit_files(db):
    """
    File to edit should be correctly edited in bulk from given data.
    """
    now = timezone.now()
    yesterday = now - datetime.timedelta(days=1)
    tomorrow = now + datetime.timedelta(days=1)

    loader = DumpLoader()

    # Create existing MediaFile objects
    mediafile_s01e01 = MediaFileFactory(
        path="/videos/BillyBoy_S01E01.mkv",
        filesize=100,
    )
    mediafile_s01e02 = MediaFileFactory(
        path="/videos/BillyBoy_S01E02.mp4",
        filesize=200,
    )
    mediafile_s01e03 = MediaFileFactory(
        path="/videos/BillyBoy_S01E03.mkv",
        filesize=300,
    )
    mediafile_s01e04 = MediaFileFactory(
        path="/videos/BillyBoy_S01E04.mkv",
        filesize=400,
    )

    # Create dumped files
    dump_s01e01 = DumpedFileFactory(
        path="/videos/BillyBoy_S01E01.mkv",
        mediafile=mediafile_s01e01,
        extension="mp4",
        size=101,
    )
    dump_s01e02 = DumpedFileFactory(
        path="/videos/BillyBoy_S01E02.mp4",
        mediafile=mediafile_s01e02,
        extension="mkv",
        size=201,
    )
    dump_s01e03 = DumpedFileFactory(
        path="/videos/BillyBoy_S01E03.mkv",
        mediafile=mediafile_s01e03,
        size=301,
        mtime=tomorrow.isoformat(),
    )

    # Edit MediaFile objects corresponding to dumped files
    loader.edit_files([
        dump_s01e01,
        dump_s01e02,
        dump_s01e03,
    ], batch_date=yesterday)

    assert MediaFile.objects.count() == 4
    assert MediaFile.objects.filter(loaded_date=yesterday).count() == 3

    # Ensure each difference have been applied and nothing have been dropped
    fetched_s01e01 = MediaFile.objects.get(path=mediafile_s01e01.path)
    assert fetched_s01e01.filesize == 101
    assert fetched_s01e01.container == "mp4"

    fetched_s01e02 = MediaFile.objects.get(path=mediafile_s01e02.path)
    assert fetched_s01e02.filesize == 201
    assert fetched_s01e02.container == "mkv"

    fetched_s01e03 = MediaFile.objects.get(path=mediafile_s01e03.path)
    assert fetched_s01e03.filesize == 301
    assert fetched_s01e03.stored_date == tomorrow


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

    # Ensure each difference have been applied and nothing have been dropped
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
