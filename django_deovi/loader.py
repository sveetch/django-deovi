"""
==================
Deovi dump manager
==================

"""
import json

from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.validators import validate_slug
from django.utils import timezone

from .dump import DumpedFile
from .models import Device, Directory, MediaFile
from .outputs import BaseOutput


class DumpLoader:
    """
    Load files datas from a dump of directories.

    File with a path which already exists in database are considered to be updated
    since MediaFile.path have an 'unique' constraint. The other files will be created.

    Since device is not a concept from Deovi and only at Django Deovi level, a dump
    is only about directories and files from a single device. There is no way to import
    dump content for many devices.

    Attributes:
        EDITABLE_FIELDS (list): Only those MediaFile fields are allowed to be edited
            from loaded payload. Field 'loaded_date' should never be editable since it
            is already forced from 'create_files' and 'edit_files' methods.

    Keyword Arguments:
        batch_limit (integer): Limit of entries to create or update in a single batch
            during bulk operations. If entry length is over the limit, they will be
            divided to multiple batches.
        output_interface (django_deovi.outputs.BaseOutput): The interface to use to
            output operation messages. It defaults on the basic interface which use
            Python logging.
    """
    EDITABLE_FIELDS = [
        "filename", "absolute_dir", "container", "filesize", "stored_date"
    ]

    def __init__(self, batch_limit=None, output_interface=None):
        self.batch_limit = batch_limit
        self.log = output_interface or BaseOutput()

    def open_dump(self, dump):
        """
        Arguments:
            dump (pathlib.Path or dict): Either directly the dump dictionnary or a path
                object for the dump file to load.

        Returns:
            dict: A dictionnary of directories from dump.
        """
        if isinstance(dump, dict):
            return dump

        return json.loads(dump.read_text())

    def get_existing(self, directory, files):
        """
        Retrieve and return every existing MediaFile for the given couple device+path.

        Arguments:
            directory (django_deovi.models.Directory): Directory object to assign all
                the files.
            files (list): List of dictionnaries for directory children files.

        Returns:
            dict: A dictionnary where each item key is a path and item value is the
                related MediaFile object.
        """
        paths = [item["path"] for item in files]

        existing = MediaFile.objects.filter(
            directory=directory,
            path__in=paths,
        ).order_by("path")

        return {
            item.path: item
            for item in existing
        }

    def create_files(self, directory, files, batch_date):
        """
        Create dump files in database using a bulk creation.

        NOTE: Remember that bulk discard the save() method.

        Arguments:
            directory (django_deovi.models.Directory): Directory object to assign all
                the files.
            files (list): List of DumpedFile objects for directory children files.
            batch_date (datetime.datetime): A datetime object to fill
                ``MediaFile.loaded_date`` field value. It is used to ensure all the
                files loaded from the directory have the same update date.
        """
        self.log.debug("- Proceed to bulk creation")

        MediaFile.objects.bulk_create([
            MediaFile(
                **item.convert_to_orm_fields(),
                loaded_date=batch_date,
                directory=directory,
            )
            for item in files
        ], batch_size=self.batch_limit)

    def edit_files(self, files, batch_date):
        """
        Create dump files in database using a bulk edition.

        This operation method does not care about directory since it is not an editable
        field from a dump loading.

        NOTE: Remember that bulk discard the save() method.

        NOTE:
            Performance could be better with a diff implementation to know the fields
            that have really changed and to avoid to always edit all allowed fields.
            Especially since the common updates will probably be on some few fields
            (like size or date).

            Also, any file from given batch files will be edited even if it does not
            have any changes.

        Arguments:
            files (list): List of DumpedFile objects for directory children files.
                Opposed to ``create_files``, the DumpedFile objects are expected to
                transport a MediaFile object which have been retrieved during
                distribution. This object will be used to proceed to bulk update.
            batch_date (datetime.datetime): A datetime object to fill
                ``MediaFile.loaded_date`` field value. It is used to ensure all the
                files loaded from the directory have the same update date.
        """
        self.log.debug("- Proceed to bulk edition")

        bulk_items = []

        for item in files:
            # This may not be really useful since this requirement is correctly
            # documented and there is no direct user input here.
            try:
                assert isinstance(item._mediafile, MediaFile) is True
            except AssertionError:
                msg = "Entry was missing original MediaFile object: {}"
                self.log.critical(msg.format(item.path))

            # Apply new values on object fields from dumped file data
            for name, value in item.convert_to_orm_fields().items():
                # Update all available field attributes
                if name in self.EDITABLE_FIELDS:
                    setattr(item._mediafile, name, value)
                # Force the loaded date from the batch date
                setattr(item._mediafile, "loaded_date", batch_date)

                bulk_items.append(item._mediafile)

        # Proceed to the bulk update
        MediaFile.objects.bulk_update(
            bulk_items,
            self.EDITABLE_FIELDS + ["loaded_date"]
        )

    def file_distribution(self, directory, files):
        """
        Distribute file entry for creation or edition depending if their path already
        exists in database or not.

        Arguments:
            directory (django_deovi.models.Directory): Directory object to assign all
                the files.
            files (list): List of dictionnaries for directory children files.

        Returns:
            tuple: List of "to create" file items and list of "to edit" file items.
            File item is the file payload as retrieved from dump.
        """
        # Find existing file paths from db
        existing = self.get_existing(directory, files)
        if len(existing) > 0:
            msg = "- Found {} existing MediaFile objects related to this dump"
            self.log.info(msg.format(len(existing)))

        # Push non existing items to the creation list
        to_create = [
            DumpedFile(**item) for item in files
            if item["path"] not in existing
        ]
        if len(to_create) > 0:
            self.log.info("- Files entry to create: {}".format(len(to_create)))

        # Push existing items to the edition list
        to_edit = [
            DumpedFile(**item, mediafile=existing[item["path"]]) for item in files
            if item["path"] in existing
        ]
        if len(to_edit) > 0:
            self.log.info("- Files entry to edit: {}".format(len(to_edit)))

        return to_create, to_edit

    def _is_directory_elligible(self, from_checksum, to_checksum, created):
        """
        Check if directory is elligible to write operation depending its checksum
        and creation state.

        * Whatever checksum if item is created, it must be elligible;
        * If any of checksum is empty, item is elligible;
        * If item is not created (edited), if checksum differ, item is elligible;

        Arguments:
            from_checksum (string): Current object checksum.
            to_checksum (string): Checksum to compare against ``from_checksum``.
            created (boolean): Define if method is called for a new created object or
                not.

        Returns:
            boolean: True if object is elligible to write operation or not.
        """
        if created:
            return True

        if not from_checksum or not to_checksum:
            return True

        return from_checksum != to_checksum

    def get_attached_file(self, path, basepath=None):
        """
        Try to get file from given path and return a Django File object ready
        to save in model.

        Arguments:
            path (string or pathlib.Path): Path to the file to get. Path string will
                be converted to Path object.
            basepath (pathlib.Path): Base directory path used to resolve relative path.

        Returns:
            django.core.files.File: Django file object filled with file from resolved
            path.
        """
        if path:
            # Convert to Path object if needed
            if isinstance(path, str):
                path = Path(path)

            # Prefix relative path with basepath if given
            filepath = path
            if not path.is_absolute() and basepath:
                filepath = basepath / path

            if not filepath.exists():
                self.log.warning("📄 Unable to find file: {}".format(path))
            else:
                # Build a Django File ready to save
                return File(filepath.open("rb"), name=filepath)

        return None

    def process_directory(self, device, directories, covers_basepath):
        """
        Process a directory entry from a dump to create Directory and process its
        children files.

        .. NOTE::
            Deovi provide a checksum for the cover file itself but we don't implement
            it, we just care about the directory checksum. Since checksum is computed
            from a resume from directory and its mediafiles details, any change trigger
            a new checksum and so it is safe to stand on it.

        Arguments:
            device (django_deovi.models.Device): Device object to assign all the files.
            directories (dict): Dictionnary of dumped directories.
            covers_basepath (pathlib.Path):

        Returns:
            list: List of tuple for each saved directory. Tuple has two elements, the
            directory object and boolean for creation state.
        """
        saved = []

        for dump_dir_name, dump_dir_data in directories.items():
            batch_date = timezone.now()

            self.log.info("📂 Working on directory: {}".format(dump_dir_data["path"]))
            directory, created = Directory.objects.update_or_create(
                device=device,
                path=dump_dir_data["path"],
            )

            # Don't process directory (and its mediafiles) if not elligible
            if not self._is_directory_elligible(
                directory.checksum, dump_dir_data.get("checksum"), created=None
            ):
                continue

            # Save additional directory data
            if created:
                self.log.debug("- New directory created")
                directory.title = dump_dir_data.get("title", "")
                directory.checksum = dump_dir_data.get("checksum", "")
                directory.cover = self.get_attached_file(
                    dump_dir_data.get("cover"),
                    basepath=covers_basepath,
                )
                # TODO: Payload should not include everything, only what has not been
                # filled in model fields
                directory.payload = json.dumps(dump_dir_data)
                directory.save()
            else:
                self.log.debug("- Got an existing directory")
                if directory.checksum != dump_dir_data.get("checksum", ""):
                    directory.title = dump_dir_data.get("title", "")
                    directory.checksum = dump_dir_data.get("checksum", "")
                    directory.cover = self.get_attached_file(
                        dump_dir_data.get("cover"),
                        basepath=covers_basepath,
                    )
                    directory.payload = json.dumps(dump_dir_data)
                    directory.save()

            # Distribute file to bulk chains
            to_create, to_edit = self.file_distribution(
                directory, dump_dir_data["children_files"]
            )

            if len(to_create) > 0:
                self.create_files(directory, to_create, batch_date=batch_date)

            if len(to_edit) > 0:
                self.edit_files(to_edit, batch_date=batch_date)

            if len(to_create) > 0 or len(to_edit) > 0:
                saved.append((directory, created))

        return saved

    def set_device_stats(self, device, stats):
        """
        Set device disk usage values.

        This will try to no update the device if no usage values have changed to avoid
        triggering ``Device.last_update`` date change.

        Arguments:
            device (django_deovi.models.Device): Device object to update.
            stats (dict): Dictionnary of disk usage items from dump.

        Returns:
            bool: True if device has been updated else False.
        """
        changed = False

        if device.disk_total != stats["total"]:
            device.disk_total = stats["total"]
            changed = True

        if device.disk_used != stats["used"]:
            device.disk_used = stats["used"]
            changed = True

        if device.disk_free != stats["free"]:
            device.disk_free = stats["free"]
            changed = True

        if changed:
            device.save()

        return changed

    def load(self, device_slug, dump, covers_basepath=None):
        """
        Load a Deovi dump to create and update MediaFile objects for the dump directory
        and files.

        Arguments:
            device_slug (string): Slug name for the Device object to attach all the
                directories and files.
            dump (pathlib.Path): The path object for the dump file to load.

        Keyword Arguments:
            covers_basepath (pathlib.Path): A path object to use to resolve cover
                filepath. If empty, the current working directory is used. Finally
                every cover files paths are resolved from this base dir.
        """
        self.log.info("🏷️Using device slug: {}".format(device_slug))

        try:
            validate_slug(device_slug)
        except ValidationError as e:
            self.log.critical("Invalid device slug: {}".format("; ".join(e)))

        # Get existing device from slug if any else create a new one using slug as the
        # default title
        device, created = Device.objects.get_or_create(
            slug=device_slug,
            defaults={"title": device_slug},
        )

        if created:
            msg = "- New device created for given slug"
        else:
            msg = "- Got an existing device for given slug"
        self.log.debug(msg)

        covers_basepath = covers_basepath or Path.cwd()
        self.log.info("🏷️Using cover basepath: {}".format(covers_basepath))

        dump_payload = self.open_dump(dump)
        try:
            device_stats = dump_payload["device"]
            registry = dump_payload["registry"]
        except KeyError:
            self.log.critical(
                "The JSON dump structure does not fit to Deovi>=0.7.0, it must "
                "have a 'device' and 'registry'."
            )

        # Update device with disk usage
        self.set_device_stats(device, device_stats)

        # Go collecting into device directories
        self.process_directory(device, registry, covers_basepath)
