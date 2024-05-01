import json

from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, View
from django.views.generic.detail import SingleObjectMixin
from django.template.defaultfilters import filesizeformat


from .mixins import DeoviBreadcrumMixin
from ..models import Device, Directory


class DeviceIndexView(DeoviBreadcrumMixin, ListView):
    """
    Device index
    """
    model = Device
    template_name = "django_deovi/device/index.html"
    paginate_by = settings.DEVICE_PAGINATION
    context_object_name = "device_list"
    crumb_title = _("Devices")
    crumb_urlname = "django_deovi:device-index"

    @property
    def crumbs(self):
        return [
            # (self.crumb_title, reverse(self.crumb_urlname)),
        ]

    def get_queryset(self):
        """
        Get device object
        """
        return self.model.objects.all()


class DeviceDetailView(DeoviBreadcrumMixin, SingleObjectMixin, ListView):
    """
    Device detail
    """
    model = Device
    listed_model = Directory
    template_name = "django_deovi/device/detail.html"
    paginate_by = settings.DIRECTORY_PAGINATION
    context_object_name = "device_object"
    crumb_title = None
    crumb_urlname = "django_deovi:device-detail"
    slug_url_kwarg = "device_slug"

    @property
    def crumbs(self):
        details_kwargs = {
            "device_slug": self.object.slug,
        }

        return [
            (DeviceIndexView.crumb_title, reverse(
                DeviceIndexView.crumb_urlname
            )),
            (self.object.slug, reverse(self.crumb_urlname, kwargs=details_kwargs)),
        ]

    def get_queryset_for_object(self):
        """
        Build queryset base to get Device.
        """
        return self.model.objects.all()

    def get_queryset(self):
        """
        Build queryset base to list Device directories.

        Depend on "self.object" to list the Device related objects.
        """
        return self.object.directories.order_by(*self.listed_model.COMMON_ORDER_BY)

    def get(self, request, *args, **kwargs):
        # Get Device object
        self.object = self.get_object(queryset=self.get_queryset_for_object())

        # Let the ListView mechanics manage list pagination from given queryset
        return super().get(request, *args, **kwargs)


class DeviceTreeView(DeoviBreadcrumMixin, DetailView):
    """
    Device directory tree
    """
    model = Device
    template_name = "django_deovi/device/tree.html"
    context_object_name = "device_object"
    crumb_title = None
    crumb_urlname = "django_deovi:device-tree"
    slug_url_kwarg = "device_slug"

    @property
    def crumbs(self):
        details_kwargs = {
            "device_slug": self.object.slug,
        }

        return [
            (DeviceIndexView.crumb_title, reverse(
                DeviceIndexView.crumb_urlname
            )),
            (self.object.slug, reverse(
                DeviceDetailView.crumb_urlname,
                kwargs=details_kwargs
            )),
            ("Tree", None),
        ]

    def get_queryset(self):
        """
        Build queryset base to get Device.
        """
        return self.model.objects.all()


class DeviceTreeExportView(SingleObjectMixin, View):
    """
    A view to receive a POST request with JSON data to proceed on a required task.

    This only accept HTTP method 'POST' with JSON data and respond with JSON response,
    except for errors which are still multipart content.

    Task to perform is selected in request data item 'action' which is a string value
    to match one of available task names from ``DeviceTreeExportView.task_actions``.

    Request data must also have a data item ``data`` that must be a dictionnary, where
    payload for tasks will be given. Expected task payload structure may vary from a
    task to another.

    Expected base data structure is always: ::

        {
            "action": "...",
            "data": ...
        }

    Where ``action`` is always a name available in DeviceTreeExportView attribute
    ``task_actions``. And ``data`` content depends from task.

    Implemented tasks:

    ping
        A very basic task that won't do anything except return a basic dictionnary,
        this is only for debugging purpose.

        Expected payload would be: ::

            {
                "action": "ping",
                "data": ...
            }

        With this task, the ``data`` content can be anything since we don't care about
        it.

    list-text
        Just returns a list of paths from selection in payload.

        Expected payload would be: ::

            {
                "action": "list-text",
                "data": {
                    "paths": [
                        {
                            "path": "...",
                        }
                    ]
                }
            }

        A 'paths' item can contains more fields than ``path`` but they are useless.

    details-json
        Returns the selected path detail into a dumped JSON (string).

        Expected payload would be: ::

            {
                "action": "details-json",
                "data": {
                    "paths": [
                        {
                            "path": "...",
                            "name": "...",
                            "total_files":"22",
                            "total_filesize": "9538655531",
                            "recursive_files": "22",
                            "recursive_filesize": "9538655531"
                        }
                    ]
                }
            }

        But for true, ``paths`` content structure is almost free since it is just
        dumped to JSON without any computation.

    Finally all success responses will return a payload alike: ::

        {
            "content": ...
        }

    Where ``content`` will contains action output as a string.

    """
    model = Device
    http_method_names = ["post"]
    slug_url_kwarg = "device_slug"
    task_actions = ["details-json", "list-text", "size-sum", "ping"]

    def get_queryset(self):
        """
        Build queryset base to get Device.
        """
        return self.model.objects.all()

    def post(self, request, *args, **kwargs):
        # Get Device object
        self.object = self.get_object(queryset=self.get_queryset())

        # Load data from expected JSON from request
        try:
            data = json.loads(request.body.decode("utf-8"))
        except json.decoder.JSONDecodeError:
            return HttpResponseBadRequest("Request contains invalid JSON")

        # Get expected fields from data
        task_action = data.get("action", None)
        payload = data.get("data", None)

        # Validate action field type and value
        if not task_action:
            return HttpResponseBadRequest("Request data must includes 'action' item")
        elif task_action not in self.task_actions:
            return HttpResponseBadRequest(
                "Payload field 'action' value must be an available action: {}".format(
                    ", ".join(self.task_actions)
                )
            )

        # Validate data field type
        if payload is None:
            return HttpResponseBadRequest("Request data must includes 'data' item")
        elif not isinstance(payload, dict):
            return HttpResponseBadRequest(
                "Payload field 'data' must be a dictionnary"
            )

        method_name = "action_{}".format(task_action.replace("-", "_"))
        return getattr(self, method_name)(request, payload)

    def action_ping(self, request, payload):
        """
        Just return given payload in payload item ``content``.
        """
        return JsonResponse({"content": payload})

    def action_list_text(self, request, payload):
        """
        Just returns a sorted list of paths from selection in payload.
        """
        if "paths" not in payload:
            return HttpResponseBadRequest(
                "Request data is invalid, details items must have a 'path' item"
            )

        return JsonResponse({"content": "\n".join(
            sorted([
                item["path"]
                for item in payload["paths"]
            ])
        )})

    def action_details_json(self, request, payload):
        """
        Returns the selected paths details into a dumped JSON (carried in a string).
        """
        if "paths" not in payload:
            return HttpResponseBadRequest(
                "Request data is invalid, details items must have a 'path' item"
            )

        return JsonResponse({
            "content": json.dumps(payload["paths"], indent=4)
        })

    def action_size_sum(self, request, payload):
        """
        Returns the sum of selected path sizes.
        """
        if "paths" not in payload:
            return HttpResponseBadRequest(
                "Request data is invalid, details items must have a 'path' item"
            )

        # Prepare lines from selections
        lines = [
            [
                item["name"],
                int(item["recursive_filesize"]),
                filesizeformat(item["recursive_filesize"])
            ]
            for item in payload["paths"]
        ]

        # Get the max size of name and formatted size
        name_column_width = max([len(k) for k, v, f in lines]) + 1
        size_column_width = max([len(f) for k, v, f in lines]) + 2

        # Push lines in output
        output = []
        for name, size, formatted in lines:
            output.append(
                name.ljust(name_column_width) + ":" +
                formatted.rjust(size_column_width)
            )

        # Add final divider and total sum
        output.append("-" * (name_column_width + size_column_width + 1))
        size_sum = sum([size for name, size, formatted in lines])
        output.append(
            "Total".ljust(name_column_width) + ":" +
            filesizeformat(size_sum).rjust(size_column_width)
        )

        return JsonResponse({
            "content": "\n".join(output)
        })
