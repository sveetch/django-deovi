import json

from django.urls import reverse

from django_deovi.factories import DeviceFactory
from django_deovi.utils.tests import decode_response_or_string


def test_device_tree_export_base_errors(db, client):
    """
    View should properly validate everything on request structure and value
    """
    url = reverse("django_deovi:device-tree-export", kwargs={
        "device_slug": "nope",
    })
    response = client.post(url, {})
    assert response.status_code == 404

    device = DeviceFactory()

    url = reverse("django_deovi:device-tree-export", kwargs={
        "device_slug": device.slug
    })

    # Only HTTP method 'POST' is allowed
    response = client.get(url)
    assert response.status_code == 405

    # Data must be valid JSON
    response = client.post(url, "foo", content_type="application/json")
    assert response.status_code == 400
    assert response.content.decode() == "Request contains invalid JSON"

    # Request data must include item 'data' as a dict and item 'action' as a string
    response = client.post(url, {"data": "plop"}, content_type="application/json")
    assert response.status_code == 400
    assert response.content.decode() == "Request data must includes 'action' item"

    response = client.post(url, {"action": "ping"}, content_type="application/json")
    assert response.status_code == 400
    assert response.content.decode() == "Request data must includes 'data' item"

    # action value must be an available action
    response = client.post(url, {"action": "nope"}, content_type="application/json")
    assert response.status_code == 400
    assert response.content.decode() == (
        "Payload field 'action' value must be an available action: ping"
    )

    # data value must a dictionnary
    response = client.post(
        url,
        {"data": "plop", "action": "ping"},
        content_type="application/json"
    )
    assert response.status_code == 400
    assert response.content.decode() == (
        "Payload field 'data' must be a dictionnary"
    )


def test_device_tree_export_ping(db, client):
    """
    Ping action is only used for debugging a basic Request/Response and should
    succeed returning given payload in a 'back' item.
    """
    device = DeviceFactory()

    url = reverse("django_deovi:device-tree-export", kwargs={
        "device_slug": device.slug
    })

    response = client.post(
        url,
        {"data": {}, "action": "ping"},
        content_type="application/json"
    )

    assert response.status_code == 200
    json_data = response.json()
    assert json_data == {"back": {}}

    response = client.post(
        url,
        {"data": {"my": "payload"}, "action": "ping"},
        content_type="application/json"
    )

    assert response.status_code == 200
    json_data = response.json()
    # print()
    # print(json.dumps(json_data, indent=4))
    assert json_data == {"back": {"my": "payload"}}
