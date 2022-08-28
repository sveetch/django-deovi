import datetime
import logging

import pytest

from django.db.utils import IntegrityError
from django.db import transaction
from django.utils import timezone

from django_deovi import __pkgname__
from django_deovi.models import MediaFile
from django_deovi.factories import DeviceFactory, DumpedFileFactory, MediaFileFactory
from django_deovi.loader import DumpLoader


def test_dumploader_get_existing(db, caplog):
    """
    Method should return every MediaFile corresponding to the given couple
    device + path.
    """
    caplog.set_level(logging.DEBUG, logger=__pkgname__)

    device_primary = DeviceFactory(title="Primary", slug="primary")
    device_secondary = DeviceFactory(title="Secondary", slug="secondary")

    loader = DumpLoader()

    # Videos which will be found as existing
    picsou = MediaFileFactory(device=device_primary, path="/videos/picsou.mkv")
    donald = MediaFileFactory(device=device_primary, path="/videos/donald.mkv")
    picsou_bis = MediaFileFactory(device=device_primary, path="/home/videos/picsou.mkv")
    # Some other videos for filling
    MediaFileFactory(device=device_primary, path="/home/videos/donald.mkv")
    MediaFileFactory(device=device_secondary, path="/videos/donald.mkv")
    MediaFileFactory(device=device_secondary, path="/videos/daisy.mkv")

    existing = loader.get_existing(device_primary, [
        {"path": "/home/donald.mkv"},
        {"path": "/home/videos/picsou.mkv"},
        {"path": "/videos/daisy.mkv"},
        {"path": "/videos/donald.mkv"},
        {"path": "/videos/picsou.mkv"},
    ])

    assert existing == {
        picsou.path: picsou,
        donald.path: donald,
        picsou_bis.path: picsou_bis,
    }


def test_dumploader_file_distribution(db, caplog):
    """
    Given dumped files should be correctly distribued to edition and creation queue
    lists respectively whether if they already exist in database or not.
    """
    caplog.set_level(logging.DEBUG, logger=__pkgname__)

    device = DeviceFactory(title="Master", slug="master")

    loader = DumpLoader()

    # Create existing MediaFile objects
    MediaFileFactory(
        device=device,
        path="/videos/BillyBoy_S01E01.mkv",
        filesize=1105021329,
    )
    MediaFileFactory(
        device=device,
        path="/videos/BillyBoy_S01E02.mkv",
        filesize=777051908,
    )
    MediaFileFactory(
        device=device,
        path="/videos/BillyBoy_S01E03.mkv",
        filesize=906120796,
    )
    MediaFileFactory(
        device=device,
        path="/videos/BillyBoy_S02E01.mkv",
        filesize=1024,
    )

    # Create dump files
    dump_s01e01 = DumpedFileFactory(path="/videos/BillyBoy_S01E01.mkv")
    dump_s01e03 = DumpedFileFactory(path="/videos/BillyBoy_S01E03.mkv")
    dump_s01e04 = DumpedFileFactory(path="/videos/BillyBoy_S01E04.mkv")

    # Distribute a dump of not yet loaded files
    to_create, to_edit = loader.file_distribution(device, [
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

    device = DeviceFactory(title="Master", slug="master")

    loader = DumpLoader()

    # Create dump files
    BillyBoy_S01E01 = DumpedFileFactory(path="/videos/BillyBoy_S01E01.mkv")
    BillyBoy_S01E03 = DumpedFileFactory(path="/videos/BillyBoy_S01E03.mkv")
    BillyBoy_S01E04 = DumpedFileFactory(path="/videos/BillyBoy_S01E04.mkv")

    # Distribute a dump of not yet loaded files
    loader.create_files(device, [
        BillyBoy_S01E01,
        BillyBoy_S01E03,
        BillyBoy_S01E04,
    ], batch_date=yesterday)

    assert MediaFile.objects.count() == 3
    assert MediaFile.objects.filter(loaded_date=yesterday).count() == 3


def test_dumploader_create_uniqueness_path(db):
    """
    MediaFile device + path uniqueness constraint should make the bulk chain to fail.

    TODO: This does not test the real uniqueness constraint, only the path uniqueness
    for the same device.
    """
    now = timezone.now()

    device = DeviceFactory(title="Primary", slug="primary")

    loader = DumpLoader()

    # Create the dumps to pass to bulk chain
    dump_first = DumpedFileFactory(path="/videos/foo_1.mkv")
    dump_second = DumpedFileFactory(path="/videos/foo_2.mkv")
    dump_third = DumpedFileFactory(path="/videos/foo_2.mkv")

    # Create the first dump file as an existing MediaFile object
    media_first = MediaFileFactory(
        device=device,
        **dump_first.convert_to_orm_fields()
    )

    # Against existing objects
    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            loader.create_files(device, [
                dump_first,
                dump_second,
            ], batch_date=now)

        assert str(excinfo.value) == (
            "UNIQUE constraint failed: django_deovi_mediafile.device_id, "
            "django_deovi_mediafile.path"
        )

    # The transaction don't let pass anything that was in the failed chain, there is
    # only the previously existing object
    assert MediaFile.objects.count() == 1

    # TODO: Against identical couple inside the bulk chain
    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            loader.create_files(device, [
                dump_third,
                dump_third,
            ], batch_date=now)

        assert str(excinfo.value) == (
            "UNIQUE constraint failed: django_deovi_mediafile.device_id, "
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

    device = DeviceFactory(title="Master", slug="master")

    loader = DumpLoader(batch_limit=2)

    # Create dump files
    BillyBoy_S01E01 = DumpedFileFactory(path="/videos/BillyBoy_S01E01.mkv")
    BillyBoy_S01E02 = DumpedFileFactory(path="/videos/BillyBoy_S01E02.mkv")
    BillyBoy_S01E03 = DumpedFileFactory(path="/videos/BillyBoy_S01E03.mkv")
    BillyBoy_S01E04 = DumpedFileFactory(path="/videos/BillyBoy_S01E04.mkv")

    # Distribute a dump of not yet loaded files
    loader.create_files(device, [
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


def test_dumploader_load(db, caplog, tests_settings):
    """
    Loader should correctly load files from given dump.
    """
    caplog.set_level(logging.DEBUG, logger=__pkgname__)

    dump_path = tests_settings.fixtures_path / "dump_series.json"

    device = DeviceFactory(title="Master", slug="master")

    # Create existing MediaFile objects
    BillyBoy_S01E01 = MediaFileFactory(
        path="/videos/series/BillyBoy/BillyBoy_S01E01.mkv",
        device=device,
        filesize=100,
    )
    BillyBoy_S01E03 = MediaFileFactory(
        path="/videos/series/BillyBoy/BillyBoy_S01E03.mkv",
        device=device,
        filesize=300,
    )
    BillyBoy_S02E01 = MediaFileFactory(
        path="/videos/series/BillyBoy/BillyBoy_S02E01.mkv",
        device=device,
    )
    Coucou_1982 = MediaFileFactory(
        path="/videos/theatre/Coucou_1982.avi",
        device=device,
        filesize=1982,
    )

    # Distribute a dump of not yet loaded files
    loader = DumpLoader()
    loader.load(device, dump_path)

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
