import pytest

from django.db.utils import IntegrityError
from django.db import transaction
from django.utils import timezone

from django_deovi.models import MediaFile
from django_deovi.factories import DumpedFileFactory, MediaFileFactory
from django_deovi.loader import DumpLoader


def test_dumploader_file_distribution(db):
    """
    Given dumped files should be correctly distribued to edition and creation queue
    lists respectively whether if they already exist in database or not.
    """
    loader = DumpLoader()

    assert MediaFile.objects.all().count() == 0

    # Create media file object
    file_s01e01 = MediaFileFactory(
        path="/videos/series/BillyBoy/BillyBoy_S01E01.mkv",
        filesize=1105021329,
    )
    file_s01e02 = MediaFileFactory(
        path="/videos/series/BillyBoy/BillyBoy_S01E02.mkv",
        filesize=777051908,
    )
    file_s01e03 = MediaFileFactory(
        path="/videos/series/BillyBoy/BillyBoy_S01E03.mkv",
        filesize=906120796,
    )
    file_s02e01 = MediaFileFactory(
        path="/videos/series/BillyBoy/BillyBoy_S02E01.mkv",
        filesize=1024,
    )

    foo = DumpedFileFactory(path="/videos/series/BillyBoy/BillyBoy_S01E01.mkv")
    bar = DumpedFileFactory(path="/videos/series/BillyBoy/BillyBoy_S01E01.mkv")

    # Create dump files
    dump_s01e01 = DumpedFileFactory(path="/videos/series/BillyBoy/BillyBoy_S01E01.mkv")
    dump_s01e03 = DumpedFileFactory(path="/videos/series/BillyBoy/BillyBoy_S01E03.mkv")
    dump_s01e04 = DumpedFileFactory(path="/videos/series/BillyBoy/BillyBoy_S01E04.mkv")

    # Distribute a dump of not yet loaded files
    to_create, to_edit = loader.file_distribution([
        dump_s01e01.to_dict(),
        dump_s01e03.to_dict(),
        dump_s01e04.to_dict(),
    ])

    assert to_create == [dump_s01e04]
    assert to_edit == [dump_s01e01, dump_s01e03]


def test_dumploader_create_files(db):
    """
    File to create should be correctly created in bulk from given data.
    """
    loader = DumpLoader()

    # Create dump files
    dump_s01e01 = DumpedFileFactory(path="/videos/series/BillyBoy/BillyBoy_S01E01.mkv")
    dump_s01e03 = DumpedFileFactory(path="/videos/series/BillyBoy/BillyBoy_S01E03.mkv")
    dump_s01e04 = DumpedFileFactory(path="/videos/series/BillyBoy/BillyBoy_S01E04.mkv")

    # Distribute a dump of not yet loaded files
    loader.create_files([
        dump_s01e01,
        dump_s01e03,
        dump_s01e04,
    ])

    assert MediaFile.objects.count() == 3


def test_dumploader_create_uniqueness_path(db):
    """
    MediaFile.path uniqueness constraint should be respected inside the bulk chain.
    """
    loader = DumpLoader()

    dump_first = DumpedFileFactory(path="/videos/series/BillyBoy/BillyBoy_S01E01.mkv")
    dump_bis = DumpedFileFactory(path="/videos/series/BillyBoy/BillyBoy_S01E01.mkv")

    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            loader.create_files([
                DumpedFileFactory(path="/videos/series/BillyBoy/BillyBoy_S01E01.mkv"),
                DumpedFileFactory(path="/videos/series/BillyBoy/BillyBoy_S01E01.mkv"),
            ])

        assert str(excinfo.value) == (
            "UNIQUE constraint failed: django_deovi_mediafile.path"
        )

    # The transaction don't let pass anything that was in the failed chain
    assert MediaFile.objects.count() == 0


def test_dumploader_batch_limit(db):
    """
    The bulk limit should be respected if given and will create all items anyway.
    """
    loader = DumpLoader(batch_limit=2)

    # Create dump files
    dump_s01e01 = DumpedFileFactory(path="/videos/series/BillyBoy/BillyBoy_S01E01.mkv")
    dump_s01e02 = DumpedFileFactory(path="/videos/series/BillyBoy/BillyBoy_S01E02.mkv")
    dump_s01e03 = DumpedFileFactory(path="/videos/series/BillyBoy/BillyBoy_S01E03.mkv")
    dump_s01e04 = DumpedFileFactory(path="/videos/series/BillyBoy/BillyBoy_S01E04.mkv")

    # Distribute a dump of not yet loaded files
    loader.create_files([
        dump_s01e01,
        dump_s01e02,
        dump_s01e03,
        dump_s01e04,
    ])

    assert MediaFile.objects.count() == 4


#@pytest.mark.xfail(reason="Refactor file_distribution is needed to use in_bulk to ship retrieved object along path because bulk_update require object to change")
def test_dumploader_edit_files(db):
    """
    File to create should be correctly created in bulk from given data.
    """
    loader = DumpLoader()

    # Create existing MediaFile objects
    mediafile_s01e01 = MediaFileFactory(
        path="/videos/series/BillyBoy/BillyBoy_S01E01.mkv",
        filesize=100,
    )
    mediafile_s01e02 = MediaFileFactory(
        path="/videos/series/BillyBoy/BillyBoy_S01E02.mkv",
        filesize=200,
    )
    mediafile_s01e03 = MediaFileFactory(
        path="/videos/series/BillyBoy/BillyBoy_S01E03.mkv",
        filesize=300,
    )

    # Create dump files
    dump_s01e01 = DumpedFileFactory(
        path="/videos/series/BillyBoy/BillyBoy_S01E01.mkv",
        mediafile=mediafile_s01e01,
    )
    dump_s01e02 = DumpedFileFactory(
        path="/videos/series/BillyBoy/BillyBoy_S01E02.mkv",
        mediafile=mediafile_s01e02,
    )
    dump_s01e03 = DumpedFileFactory(
        path="/videos/series/BillyBoy/BillyBoy_S01E03.mkv",
        mediafile=mediafile_s01e03,
    )

    # Distribute a dump of not yet loaded files
    loader.edit_files([
        dump_s01e01,
        dump_s01e02,
        dump_s01e03,
    ])

    assert MediaFile.objects.count() == 3

    # Everything before is passing without errors but we need to ensure all fields
    # values have been changed as expected.
    assert 1 == 42
