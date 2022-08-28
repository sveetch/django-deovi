"""
==================
Deovi dump manager
==================

"""
import json

from pathlib import Path

from django.utils import timezone

from .dump import DumpedFile
from .models import MediaFile
from .outputs import BaseOutput
from .serializers import MediaFileSerializer


class DumpLoader:
    """
    Load files datas from a dump of directories.

    File with a path which already exists in database are considered to be updated
    since MediaFile.path have an 'unique' constraint. The other files will be created.

    Keyword Arguments:
        batch_limit (integer): Limit of entries to create or update in a single batch
            during bulk operations. If entry length is over the limit, they will be
            divided to multiple batches.
        output_interface (django_deovi.outputs.BaseOutput): The interface to use to
            output operation messages. It defaults on the basic interface which use
            Python logging.
    """
    # Only those MediaFile fields are allowed to be edited from dumped file data
    # Field 'loaded_date' should never be editable since it is already forced from
    # 'create_files' and 'edit_files' methods.
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

    def file_distribution(self, files):
        """
        Distribute file entry for creation or edition depending if their path already
        exists in database or not.

        Arguments:
            files (list): List of dictionnaries for directory children files.

        Returns:
            tuple: List of "to create" file items and list of "to edit" file items.
            File item is the file payload as retrieved from dump.
        """
        paths = [item["path"] for item in files]

        # Find existing file paths from db
        existing = MediaFile.objects.order_by("path").in_bulk(paths, field_name="path")
        if len(existing) > 0:
            msg = "- Found {} existing MediaFile objects related to this dump".format(len(existing))
            self.log.info(msg)

        to_create = [
            DumpedFile(**item) for item in files
            if item["path"] not in existing
        ]

        to_edit = [
            DumpedFile(**item, mediafile=existing[item["path"]]) for item in files
            if item["path"] in existing
        ]

        if len(to_create) > 0:
            self.log.info("- Files entry to create: {}".format(len(to_create)))
        if len(to_edit) > 0:
            self.log.info("- Files entry to edit: {}".format(len(to_edit)))

        return to_create, to_edit

    def create_files(self, files, batch_date):
        """
        Create dump files in database using a bulk creation.

        NOTE: Remember that bulk discard the save() method.

        Arguments:
            files (list): List of DumpedFile objects for directory children files.
            batch_date (datetime.datetime): A datetime object to fill
                ``MediaFile.loaded_date`` field value. It is used to ensure all the
                files loaded from the directory have the same update date.
        """
        self.log.debug("- Proceed to bulk creation")

        MediaFile.objects.bulk_create([
            MediaFile(**item.convert_to_orm_fields(), loaded_date=batch_date)
            for item in files
        ], batch_size=self.batch_limit)

    def edit_files(self, files, batch_date):
        """
        Create dump files in database using a bulk edition.

        NOTE: Remember that bulk discard the save() method.

        NOTE:
            Performance could be better with a diff implementation to know the fields
            that have really changed and to avoid to always edit all allowed fields.
            Especially since the common updates will probably be on some few fields (like
            size or date).

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

    def load(self, dump):
        """
        Load a Deovi dump to create and update MediaFile objects for the dump directory
        files.

        All files from a same directory will share the same exact loaded datetime.

        Arguments:
            dump (pathlib.Path): The path object for the dump file to load.
        """
        dump_content = self.open_dump(dump)
        for directory, data in dump_content.items():
            batch_date = timezone.now()

            self.log.info("📂 Working on directory: {}".format(data["path"]))
            to_create, to_edit = self.file_distribution(data["children_files"])

            if len(to_create) > 0:
                self.create_files(to_create, batch_date=batch_date)
            if len(to_edit) > 0:
                self.edit_files(to_edit, batch_date=batch_date)
