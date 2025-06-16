import pytest

from django.template import loader

from django_deovi.factories import DirectoryFactory, MediaFileFactory
from django_deovi.utils.text import normalize_text


@pytest.mark.parametrize("source, expected", [
    (
        "Lorem ipsum",
        "Lorem ipsum"
    ),
    (
        "Élà-plôp, lorem_ipsum",
        "Ela plop lorem ipsum"
    ),
    (
        "1 apple a day, keep the doctor away!",
        "1 apple a day keep the doctor away"
    ),
    (
        "://foo/the-filename.mp4",
        "foo the filename mp4"
    ),
])
def test_normalize_text(source, expected):
    """
    Text should be correctly normalized (no unicode, no punctuation, no twice
    whitespace beetween words).
    """
    assert normalize_text(source) == expected


def test_directory_index_render():
    """
    Directory index render should only contain the normalized title
    """
    template_path = "django_deovi/search/directory_indexes_template.txt"

    assert loader.get_template(template_path).render({
        "object": DirectoryFactory.build(title="Élà-plôp, lorem_ipsum"),
    }) == "Ela plop lorem ipsum"


def test_mediafile_index_render():
    """
    MediaFile index render should contain its normalized filename
    """
    template_path = "django_deovi/search/mediafile_indexes_template.txt"

    assert loader.get_template(template_path).render({
        "object": MediaFileFactory.build(filename="lorem_ipsum.tar.mp4"),
    }) == "lorem ipsum tar"
