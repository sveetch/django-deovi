import json

from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, View
from django.views.generic.detail import SingleObjectMixin

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

    Implemented tasks:

    ping
        A very basic task that won't do anything except return a basic dictionnary,
        this is only for debugging purpose.

    list-text
        Just returns a list of paths from selection in payload.

    details-json
        Returns the selected path detail into a dumped JSON (string).

    """
    model = Device
    http_method_names = ["post"]
    slug_url_kwarg = "device_slug"
    task_actions = ["ping", "details-json", "list-text"]

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
        Just return given payload in payload item ``back``.
        """
        return JsonResponse({"back": payload})

    def action_list_text(self, request, payload):
        """
        Just returns a list of paths from selection in payload.
        """
        return JsonResponse({"content": "\n".join(
            sorted([
                item["path"]
                for item in payload["paths"]
            ])
        )})

    def action_details_json(self, request, payload):
        """
        Returns the selected path detail into a dumped JSON (string)
        """
        return JsonResponse({
            "content": json.dumps(payload["paths"], indent=4)
        })
