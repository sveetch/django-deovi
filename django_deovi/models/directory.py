import json
from pathlib import Path

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from smart_media.modelfields import SmartMediaField
from smart_media.mixins import SmartFormatMixin
from smart_media.signals import auto_purge_files_on_change, auto_purge_files_on_delete

from ..utils.text import normalize_text


class Directory(SmartFormatMixin, models.Model):
    """
    A directory container to hold MediaFile objects.

    TODO:
    * New field 'genres' collected from payload, it should be a many2many;
    * Stored payload should not include the mediafile list (loader should pop it away);
    * Payload should contains something like: ::

        tmdb_id: 14009
        tmdb_type: tv
        number_of_episodes: 64
        number_of_seasons: 2
        status: Ended

    """
    device = models.ForeignKey(
        "Device",
        verbose_name=_("Related device"),
        related_name="directories",
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
        blank=True,
        max_length=150,
        default="",
    )
    """
    Optional title string.
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

    checksum = models.CharField(
        _("checksum"),
        blank=True,
        max_length=50,
        default="",
        help_text=_(
            "A blake2 hash for directory information checksum."
        ),
    )
    """
    Optional checksum string.
    """

    cover = SmartMediaField(
        "cover image",
        max_length=255,
        null=True,
        blank=True,
        default=None,
        upload_to="directory/cover/%y/%m",
        help_text=_(
            "Directory cover image."
        ),
    )
    """
    Optional cover image.
    """

    payload = models.TextField(
        _("JSON payload"),
        blank=True,
        default="{}",
        help_text=_(
            "Extra directory informations. Structure may vary from a directory to "
            "another."
        ),
    )
    """
    Optional JSON payload for extra informations to store, they won't be searchable
    """

    created_date = models.DateTimeField(
        _("created date"),
        db_index=True,
        default=timezone.now,
        help_text=_(
            "The creation date for this object."
        ),
    )
    """
    Required datetime for when the directory has been loaded.
    """

    last_update = models.DateTimeField(
        _("last update"),
        db_index=True,
        default=timezone.now,
        help_text=_(
            "The last update date for this object."
        ),
    )
    """
    Last edition date.
    """

    released = models.DateField(
        _("released date"),
        default=None,
        null=True,
        blank=True,
        db_index=True,
        help_text=_(
            "Released/On Air date for a serie directory or video set directory. This "
            "is not related to media collection or file creation."
        ),
    )
    """
    Optional release date.
    """

    COMMON_ORDER_BY = ["path"]
    """
    List of field order commonly used in frontend view/api
    """

    class Meta:
        verbose_name = _("Directory")
        verbose_name_plural = _("Directories")
        ordering = [
            "path",
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
        return self.title or self.directory_name()

    def normalized_title(self):
        return normalize_text(self.title)

    def get_absolute_url(self):
        """
        Return absolute URL to the detail view.

        Returns:
            string: An URL.
        """
        return reverse("django_deovi:directory-detail", kwargs={
            "device_slug": self.device.slug,
            "directory_pk": self.id,
        })

    def directory_parent(self):
        """
        Return directory parent path.

        Returns:
            string: Parent path.
        """
        return str(Path(self.path).parent)

    def directory_name(self):
        """
        Return directory name from path

        Returns:
            string: Directory name.
        """
        return str(Path(self.path).name)

    def get_payload_object(self):
        """
        Return deserialized JSON payload as a Python object (a dict is always
        expected).

        Returns:
            dict: Payload as Python object.
        """
        if not self.payload:
            return {}

        return json.loads(self.payload)

    def get_genres(self):
        """
        Return stored 'genres' from payload.

        Expected 'genres' type is always a list of string.

        Returns:
            list: Always return a list, either the genre list if there is any else an
            empty list.
        """
        genres = self.get_payload_object().get("genres", [])
        genres = genres if genres and isinstance(genres, list) else []
        return [normalize_text(v) for v in genres]

    def get_air_date_year(self):
        """
        Return stored air date year.

        Expected 'first_air_date' type is always a string containing divided in three
        parts with a ``-`` and the first part is assumed to be a four digits valid
        integer.

        Returns:
            list: Either the air date year if there is any else None.
        """
        air_date = self.get_payload_object().get("first_air_date", None)
        if (
            not air_date
            or not isinstance(air_date, str)
            or len(air_date.split("-")) < 3
        ):
            return None

        year = air_date.split("-")[0]
        if len(year) < 4:
            return None
        else:
            try:
                year = int(year)
            except ValueError:
                return None

        return year

    def resume(self):
        """
        Return a resume of some directory informations.

        Payload items can not overwrite computed informations so these item names will
        be ignored: ``mediafiles``, ``filesize`` and ``last_media_update``.

        Returns:
            dict: Directory informations.
        """
        mediafiles = self.mediafiles.annotate(
            total_filesize=models.Sum("filesize"),
        )

        resume = {
            "mediafiles": len(mediafiles),
            "filesize": sum([item.total_filesize for item in mediafiles]),
            "last_media_update": sorted([item.loaded_date for item in mediafiles])[-1],
        }

        if self.payload:
            resume.update({
                k: v
                for k, v in self.get_payload_object().items()
                if k not in ("mediafiles", "filesize", "last_media_update")
            })

        return resume

    def get_cover_format(self):
        return self.media_format(self.cover)

    def clean(self):
        # If given, payload should be a valid JSON Object
        if self.payload:
            try:
                loaded = json.loads(self.payload)
            except json.decoder.JSONDecodeError:
                raise ValidationError({
                    "payload": _("Given payload is not a valid JSON format."),
                })
            else:
                if not isinstance(loaded, dict):
                    raise ValidationError({
                        "payload": _("Given payload is not a valid JSON Object."),
                    })

    def save(self, *args, **kwargs):
        # Auto update 'last_update' value on each save
        self.last_update = timezone.now()

        super().save(*args, **kwargs)


# Connect signals for automatic media purge
post_delete.connect(
    auto_purge_files_on_delete(["cover"]),
    dispatch_uid="directory_medias_on_delete",
    sender=Directory,
    weak=False,
)
pre_save.connect(
    auto_purge_files_on_change(["cover"]),
    dispatch_uid="directory_medias_on_change",
    sender=Directory,
    weak=False,
)
