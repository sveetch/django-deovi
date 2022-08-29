from django_deovi.factories import MediaFileFactory


def test_mediafile_creation(db):
    """
    Factory should correctly create a new object without any errors
    """
    mediafile = MediaFileFactory()

    assert mediafile.path.startswith("/") is True
    assert mediafile.path.endswith(mediafile.filename) is True
    assert mediafile.path.endswith(mediafile.container) is True
    assert mediafile.filesize > 0

    mediafile = MediaFileFactory(path="/home/foo/plop.avi")

    assert mediafile.filename == "plop.avi"
    assert mediafile.directory == "foo"
    assert mediafile.container == "avi"

    # TODO: MediaFile model and factory have to be modified to relate to a Directory
    # instead of a Device
    assert 1 == 42
