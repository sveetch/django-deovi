import datetime

import pytest

from django.db.utils import IntegrityError
from django.db import transaction
from django.utils import timezone

from django_deovi.models import MediaFile
from django_deovi.factories import (
    DirectoryFactory, DumpedFileFactory, MediaFileFactory
)
from django_deovi.loader import DumpLoader


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
