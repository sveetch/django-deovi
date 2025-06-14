from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from bigtree import dict_to_tree, tree_to_nested_dict

from ..utils.tree import DirectoryInfosNode


class Device(models.Model):
    """
    A device container to hold Directory objects.

    Even through it is called a device (because it is should be the common usage), it
    may be a simple directory path, therefore the disk usage will not be accurate to
    the path itself.
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

    disk_total = models.BigIntegerField(
        _("disk total"),
        blank=False,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Total available disk size of which the device belong to.",
    )
    """
    Required file size integer.
    """

    disk_used = models.BigIntegerField(
        _("disk usage"),
        blank=False,
        default=0,
        validators=[MinValueValidator(0)],
        help_text=(
            "Total used disk size of which the device belong to. This will includes"
            "the device size and everything else that belong onto the same disk."
        ),
    )
    """
    Required file size integer.
    """

    disk_free = models.BigIntegerField(
        _("disk free"),
        blank=False,
        default=0,
        validators=[MinValueValidator(0)],
        help_text=(
            "Free space size on disk of which the device belong to. This will be"
            "computed from the device size and everything else that belong onto the "
            "same disk."
        ),
    )
    """
    Required file size integer.
    """

    created_date = models.DateTimeField(
        _("created date"),
        db_index=True,
        default=timezone.now,
    )
    """
    Required datetime for when the file has been loaded.
    """

    last_update = models.DateTimeField(
        _("last update"),
        db_index=True,
        default=timezone.now,
        help_text=_(
            "The last update date for this device."
        ),
    )
    """
    Last device change date.
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
            "disk_total": self.disk_total,
            "disk_used": self.disk_used,
            "disk_free": self.disk_free,
            "disk_occupancy": (
                (self.disk_used / self.disk_total) * 100
                if self.disk_total else 0.0
            ),
            "directories": len(directories),
            "mediafiles": sum([item.num_mediafiles for item in directories]),
            "filesize": sum([item.total_filesize for item in directories]),
            "last_media_update": last_media_update,
        }

    def get_directory_tree(self):
        """
        Get recursive tree structure for all related device directories.

        Returns:
            dict: A nested tree structure of paths from parent to children. Each
            directory item will carries a payload with some informations:

            * ``filepath``: directory path;
            * ``total_files``: current directory files counter;
            * ``total_filesize``: total size of current directory files in bytes;
            * ``recursive_files``: children files counter;
            * ``recursive_filesize``: total size of children files in bytes;

            Additionally a ``children`` item can be set to a list of children
            directories if any.
        """
        # Get all device directories
        directories = self.directories.all().order_by("path")

        # Internal function to compute directory informations from its mediafiles
        def _compute_payload(directory):
            mediafiles = directory.mediafiles.annotate(
                total_filesize=models.Sum("filesize"),
            )
            return {
                "filepath": directory.path,
                "total_files": len(mediafiles),
                "total_filesize": sum([item.total_filesize for item in mediafiles]),
            }

        # Build tree from a flat dict
        tree = dict_to_tree({
            directory.path: _compute_payload(directory)
            for directory in directories
        }, node_type=DirectoryInfosNode)

        # Then export it to a nested tree structure into a dictionnary
        return tree_to_nested_dict(tree, attr_dict={
            "filepath": "filepath",
            "total_files": "total_files",
            "total_filesize": "total_filesize",
            "recursive_files": "recursive_files",
            "recursive_filesize": "recursive_filesize",
        })

    def save(self, *args, **kwargs):
        # Auto update 'last_update' value on each save
        self.last_update = timezone.now()

        super().save(*args, **kwargs)
