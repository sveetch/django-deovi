import datetime

from django.utils import timezone

from django_deovi.models import MediaFile
from django_deovi.factories import (
    DumpedFileFactory, MediaFileFactory
)
from django_deovi.loader import DumpLoader


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
