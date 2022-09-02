from django.shortcuts import get_object_or_404
from django.views.generic import ListView


from ..models import Device


class DeviceIndexView(ListView):
    """
    Device index
    """
    model = Device
    template_name = "django_deovi/device/index.html"
    paginate_by = 20
    context_object_name = "device_list"

    def get_queryset(self):
        """
        Get device object
        """
        return Device.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
