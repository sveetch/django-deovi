from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class Device(models.Model):
    """
    A device container to hold Directory objects.
    """
    title = models.CharField(
        _("title"),
        max_length=150,
        default="",
    )
    """
    Required title string.
    """

    slug = models.SlugField(
        _("slug"),
        max_length=50,
        unique=True,
        help_text=_(
            "Used to build the URL and as an argument to the loader command."
        ),
    )
    """
    Required unique slug string.
    """

    created_date = models.DateTimeField(
        _("created date"),
        db_index=True,
        default=timezone.now,
    )
    """
    Required datetime for when the file has been loaded.
    """

    COMMON_ORDER_BY = ["title"]
    """
    List of field order commonly used in frontend view/api
    """

    class Meta:
        verbose_name = _("Device")
        verbose_name_plural = _("Devices")
        ordering = [
            "title",
        ]

    def __str__(self):
        return self.slug

    def get_absolute_url(self):
        """
        Return absolute URL to the detail view.

        Returns:
            string: An URL.
        """
        return reverse("django_deovi:device-detail", kwargs={
            "device_slug": self.slug,
        })

    def resume(self):
        """
        Return a resume of some device informations.

        Returns:
            dict: Payload.
        """
        directories = self.directories.filter(device=self).annotate(
            num_mediafiles=models.Count("mediafiles"),
            total_filesize=models.Sum("mediafiles__filesize"),
            last_media_update=models.Max("mediafiles__loaded_date"),
        )
        # Get the most latter media update computed from all directories
        last_media_update = sorted([item.last_media_update for item in directories])
        if last_media_update:
            last_media_update = last_media_update[-1]
        else:
            last_media_update = None

        return {
            "directories": len(directories),
            "mediafiles": sum([item.num_mediafiles for item in directories]),
            "filesize": sum([item.total_filesize for item in directories]),
            "last_media_update": last_media_update,
        }
