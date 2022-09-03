import pytest

from tests.utils import html_pyquery

from django_deovi.factories import MediaFileFactory

@pytest.mark.xfail(reason="detail view deprecated, keep this temporarly")
def test_mediafile_detail_404(db, client):
    """
    Try to reach unexisting mediafile should return a 404 response.
    """
    url = "/1/"

    response = client.get(url)

    assert response.status_code == 404


@pytest.mark.xfail(reason="detail view deprecated, keep this temporarly")
def test_mediafile_detail_content(db, client):
    """
    MediaFile content should be displayed correctly.
    """
    mediafile = MediaFileFactory()

    url = "/{mediafile_pk}/".format(
        mediafile_pk=mediafile.id,
    )

    response = client.get(url)

    assert response.status_code == 200

    dom = html_pyquery(response)
    mediafile_path = dom.find(".mediafile-detail .path")

    assert mediafile_path.text() == mediafile.path
