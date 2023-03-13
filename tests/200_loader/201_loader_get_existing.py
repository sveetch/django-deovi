import logging

from django_deovi import __pkgname__
from django_deovi.models import MediaFile
from django_deovi.factories import (
    DeviceFactory, DirectoryFactory, MediaFileFactory
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
