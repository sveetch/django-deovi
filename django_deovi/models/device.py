"""
============
Device model
============

"""
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class Device(models.Model):
    """
    A device container to hold MediaFile objects.

    TODO: Add a field to store the device size capacity.
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

    class Meta:
        verbose_name = _("Device")
        verbose_name_plural = _("Devices")
        ordering = [
            "title",
        ]

    def __str__(self):
        return self.title
