import os

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from smart_media.modelfields import SmartMediaField
from smart_media.mixins import SmartFormatMixin
from smart_media.signals import auto_purge_files_on_change, auto_purge_files_on_delete

from ..utils.text import normalize_text


class MediaFile(SmartFormatMixin, models.Model):
    """
    A media file
    """
    directory = models.ForeignKey(
        "Directory",
        verbose_name=_("Related directory"),
        related_name="mediafiles",
        default=None,
        on_delete=models.CASCADE,
        help_text=_(
            "The directory which holds this file."
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
            "for the same directory."
        ),
    )
    """
    Required absolute file path which have to be unique along its directory. There can
    be many MediaFile objects with the same path but not related to the same Directory
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

    dirname = models.CharField(
        _("directory name"),
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

    cover = SmartMediaField(
        "cover image",
        max_length=255,
        null=True,
        blank=True,
        default=None,
        upload_to="mediafile/cover/%y/%m",
        help_text=_(
            "Media cover image."
        ),
    )
    """
    Optional cover image.
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

    COMMON_ORDER_BY = ["path"]
    """
    List of field order commonly used in frontend view/api
    """

    class Meta:
        verbose_name = _("MediaFile")
        verbose_name_plural = _("MediaFiles")
        ordering = [
            "path",
        ]
        constraints = [
            # Enforce unique couple directory + path
            models.UniqueConstraint(
                fields=[
                    "directory", "path"
                ],
                name="deovi_mediafile_directory_path"
            ),
        ]

    def __str__(self):
        return self.path

    def normalized_filename(self):
        """
        Remove ending filename extension and normalize it.
        """
        ext = os.path.splitext(self.filename)[-1]
        return normalize_text(self.filename.replace(ext, ""))

    def get_cover_format(self):
        return self.media_format(self.cover)

    def clean(self):
        # Container should not starts with a dot
        if self.container and self.container.startswith("."):
            raise ValidationError({
                "container": _("Container must not starts with a dot."),
            })


# Connect signals for automatic media purge
post_delete.connect(
    auto_purge_files_on_delete(["cover"]),
    dispatch_uid="mediafile_medias_on_delete",
    sender=MediaFile,
    weak=False,
)
pre_save.connect(
    auto_purge_files_on_change(["cover"]),
    dispatch_uid="mediafile_medias_on_change",
    sender=MediaFile,
    weak=False,
)
