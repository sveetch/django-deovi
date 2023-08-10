from django.conf import settings
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.detail import SingleObjectMixin

from ..models import Directory, MediaFile

from .device import DeviceIndexView, DeviceDetailView
from .mixins import DeoviBreadcrumMixin


class DirectoryDetailView(DeoviBreadcrumMixin, SingleObjectMixin, ListView):
    """
    Directory detail
    """
    model = Directory
    listed_model = MediaFile
    template_name = "django_deovi/directory/detail.html"
    paginate_by = settings.MEDIAFILE_PAGINATION
    context_object_name = "directory_object"
    crumb_title = None
    crumb_urlname = "django_deovi:directory-detail"
    pk_url_kwarg = "directory_pk"

    @property
    def crumbs(self):
        device_kwargs = {
            "device_slug": self.object.device.slug,
        }
        directory_kwargs = {
            "device_slug": self.object.device.slug,
            "directory_pk": self.object.id,
        }

        return [
            (DeviceIndexView.crumb_title, reverse(
                DeviceIndexView.crumb_urlname
            )),
            (self.object.device.slug, reverse(
                DeviceDetailView.crumb_urlname,
                kwargs=device_kwargs,
            )),
            (self.object, reverse(
                self.crumb_urlname,
                kwargs=directory_kwargs,
            )),
        ]

    def get_queryset_for_object(self):
        """
        Build queryset base to get Directory.
        """
        return self.model.objects.all()

    def get_queryset(self):
        """
        Build queryset base to list Directory directories.

        Depend on "self.object" to list the Directory related objects.
        """
        return self.object.mediafiles.order_by(*self.listed_model.COMMON_ORDER_BY)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["device_object"] = self.object.device

        return context

    def get(self, request, *args, **kwargs):
        # Get Directory object
        self.object = self.get_object(queryset=self.get_queryset_for_object())

        # Let the ListView mechanics manage list pagination from given queryset
        return super().get(request, *args, **kwargs)
