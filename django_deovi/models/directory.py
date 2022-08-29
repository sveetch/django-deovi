"""
============
Directory model
============

"""
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class Directory(models.Model):
    """
    A directory container to hold MediaFile objects.
    """
    device = models.ForeignKey(
        "Device",
        verbose_name=_("Related device"),
        default=None,
        on_delete=models.CASCADE,
        help_text=_(
            "The device which holds this directory."
        ),
    )
    """
    Required Device object relation.
    """

    title = models.CharField(
        _("title"),
        max_length=150,
        default="",
    )
    """
    Required title string.
    """

    path = models.TextField(
        _("path"),
        blank=False,
        default="",
        help_text=(
            "The full path where the directory is stored. There can be only an unique "
            "path for the same device."
        ),
    )
    """
    Required absolute directory path which have to be unique along its device. There can
    be many Directory objects with the same path but not related to the same Device
    object.
    """

    created_date = models.DateTimeField(
        _("created date"),
        db_index=True,
        default=timezone.now,
    )
    """
    Required datetime for when the directory has been loaded.
    """

    class Meta:
        verbose_name = _("Directory")
        verbose_name_plural = _("Directories")
        ordering = [
            "title",
        ]
        constraints = [
            # Enforce unique couple device + path
            models.UniqueConstraint(
                fields=[
                    "device", "path"
                ],
                name="deovi_directory_device_path"
            ),
        ]

    def __str__(self):
        return self.title
