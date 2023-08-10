from django_deovi.factories import DirectoryFactory, MediaFileFactory


def test_mediafile_creation(db):
    """
    Factory should correctly create a new object without any errors
    """
    mediafile = MediaFileFactory()

    assert mediafile.path.startswith("/") is True
    assert mediafile.path.endswith(mediafile.filename) is True
    assert mediafile.path.endswith(mediafile.container) is True
    assert mediafile.filesize > 0

    directory = DirectoryFactory()
    mediafile = MediaFileFactory(
        directory=directory,
        path="/home/foo/plop.avi",
    )

    assert mediafile.directory == directory
    assert mediafile.path == "/home/foo/plop.avi"
    assert mediafile.filename == "plop.avi"
    assert mediafile.dirname == "foo"
    assert mediafile.container == "avi"
