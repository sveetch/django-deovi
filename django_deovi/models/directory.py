"""
============
Directory model
============

"""
from pathlib import Path

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class Directory(models.Model):
    """
    A directory container to hold MediaFile objects.

    TODO:
    * Remove deprecated title field;
    * Need created and updated dates (may involve stopping using bulk chains);
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

    created_date = models.DateTimeField(
        _("created date"),
        db_index=True,
        default=timezone.now,
    )
    """
    Required datetime for when the directory has been loaded.
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
        return self.path

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

    def resume(self):
        """
        Return a resume of some directory informations.

        Returns:
            dict: Payload.
        """
        mediafiles = self.mediafiles.annotate(
            total_filesize=models.Sum("filesize"),
        )

        return {
            "mediafiles": len(mediafiles),
            "filesize": sum([item.total_filesize for item in mediafiles]),
        }
