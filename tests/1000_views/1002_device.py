import json

from django.urls import reverse

from django_deovi.factories import DeviceFactory
from django_deovi.views import DeviceTreeExportView


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
        "Payload field 'action' value must be an available action: {}".format(
            ", ".join(DeviceTreeExportView.task_actions)
        )
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
    succeed returning given payload in a 'content' item.
    """
    device = DeviceFactory()

    url = reverse("django_deovi:device-tree-export", kwargs={
        "device_slug": device.slug
    })

    response = client.post(
        url,
        {"action": "ping", "data": {}},
        content_type="application/json"
    )

    assert response.status_code == 200
    json_data = response.json()
    assert json_data == {"content": {}}

    response = client.post(
        url,
        {"action": "ping", "data": {"my": "payload"}},
        content_type="application/json"
    )

    assert response.status_code == 200
    json_data = response.json()
    # print()
    # print(json.dumps(json_data, indent=4))
    assert json_data == {"content": {"my": "payload"}}


def test_device_tree_export_list_text(db, client):
    """
    'List text' action should returns a sorted list of paths from given payload.
    """
    device = DeviceFactory()

    url = reverse("django_deovi:device-tree-export", kwargs={
        "device_slug": device.slug
    })

    response = client.post(
        url,
        {"data": {}, "action": "list-text"},
        content_type="application/json"
    )

    assert response.status_code == 400
    assert response.content.decode() == (
        "Request data is invalid, details items must have a 'path' item"
    )

    response = client.post(
        url,
        {
            "action": "list-text",
            "data": {
                "paths": [
                    {"path": "/foo"},
                    {"path": "/bar"},
                    {"path": "/ping/pong"},
                ]
            },
        },
        content_type="application/json"
    )

    assert response.status_code == 200
    json_data = response.json()
    # print()
    # print(json.dumps(json_data, indent=4))
    assert json_data == {
        "content": "/bar\n/foo\n/ping/pong"
    }


def test_device_tree_export_details_json(db, client):
    """
    'Details JSON' action should returns a JSON dump of given path details.
    """
    device = DeviceFactory()

    url = reverse("django_deovi:device-tree-export", kwargs={
        "device_slug": device.slug
    })

    response = client.post(
        url,
        {"data": {}, "action": "details-json"},
        content_type="application/json"
    )

    assert response.status_code == 400
    assert response.content.decode() == (
        "Request data is invalid, details items must have a 'path' item"
    )

    response = client.post(
        url,
        {
            "action": "details-json",
            "data": {
                "paths": [
                    {"path": "/foo"},
                    {"path": "/bar", "plip": "plop"},
                    {"path": "/ping/pong"},
                ]
            },
        },
        content_type="application/json"
    )

    assert response.status_code == 200
    json_data = response.json()
    # print()
    # print(json.dumps(json_data, indent=4))
    assert json_data == {
        "content": json.dumps(
            [
                {"path": "/foo"},
                {"path": "/bar", "plip": "plop"},
                {"path": "/ping/pong"},
            ],
            indent=4
        )
    }
