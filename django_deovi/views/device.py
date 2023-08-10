from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
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
