"""
=====
Media
=====

"""
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.core.validators import MinValueValidator

from deovi.collector import MEDIAS_CONTAINERS


class MediaFile(models.Model):
    """
    A media file

    TODO:
        Relate to a Directory instead of a Device.
    """
    device = models.ForeignKey(
        "Device",
        verbose_name=_("Related device"),
        default=None,
        on_delete=models.CASCADE,
        help_text=_(
            "The device which holds this file."
        ),
    )
    """
    Required Device object relation.
    """

    title = models.CharField(
        _("title"),
        blank=True,
        max_length=150,
        default="",
        help_text="Title label",
    )
    """
    Optional title string. Only used if filled, else the file name is commonly
    displayed instead
    """

    path = models.TextField(
        _("path"),
        blank=False,
        default="",
        help_text=(
            "The full path where the file is stored. There can be only an unique path "
            "for the same device."
        ),
    )
    """
    Required absolute file path which have to be unique along its device. There can be
    many MediaFile objects with the same path but not related to the same Device
    object.
    """

    absolute_dir = models.CharField(
        _("absolute directory path"),
        blank=False,
        max_length=150,
        default="",
        help_text="The absolute directory path where the file is stored",
    )
    """
    Required filename string.
    """

    directory = models.CharField(
        _("directory"),
        blank=True,
        max_length=200,
        default="",
        help_text="The directory name where file is stored.",
    )
    """
    Optionnal directory name string. This field should be an empty string only for a
    file located at root from basedir.
    """

    filename = models.CharField(
        _("filename"),
        blank=False,
        max_length=150,
        default="",
        help_text="The file name",
    )
    """
    Required filename string.
    """

    container = models.CharField(
        _("media container"),
        blank=False,
        max_length=50,
        default="",
        help_text="The media container as determined from its file extension.",
    )
    """
    Required media container file extension string.
    TODO: Should be validated to not starts with a dot since we don't want it.
    """

    filesize = models.BigIntegerField(
        _("filesize"),
        blank=False,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="The file size",
    )
    """
    Required file size integer.
    """

    stored_date = models.DateTimeField(
        _("stored date"),
        blank=False,
        db_index=True,
        default=None,
    )
    """
    Required datetime for when the file has been stored.
    """

    loaded_date = models.DateTimeField(
        _("loaded date"),
        db_index=True,
        default=timezone.now,
    )
    """
    Required datetime for when the file has been loaded.
    """

    class Meta:
        verbose_name = _("MediaFile")
        verbose_name_plural = _("MediaFiles")
        ordering = [
            "stored_date",
        ]
        constraints = [
            # Enforce unique couple device + path
            # TODO: Change to be couped to directory
            models.UniqueConstraint(
                fields=[
                    "device", "path"
                ],
                name="deovi_mediafile_device_path"
            ),
        ]

    def __str__(self):
        return self.path
