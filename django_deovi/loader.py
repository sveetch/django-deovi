"""
==================
Deovi dump manager
==================

"""
import json

from pathlib import Path

from .models import MediaFile
from .serializers import MediaFileSerializer
from .dump import DumpedFile


class DumpLoader:
    """
    Load files datas from a dump of directories.

    NOTE:
        Should be able to smartly load dump entries, meaning create a new entry only
        if it does not exists yet, else update it.
    """
    # Only thos MediaFile fields are allowed to be edited from dumped file data
    EDITABLE_FIELDS = [
        "filename", "absolute_dir", "container", "filesize", "stored_date"
    ]

    def __init__(self, batch_limit=None):
        self.batch_limit = batch_limit

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

        to_create = [
            DumpedFile(**item) for item in files
            if item["path"] not in existing
        ]

        to_edit = [
            DumpedFile(**item, mediafile=existing[item["path"]]) for item in files
            if item["path"] in existing
        ]

        return to_create, to_edit

    def create_files(self, files):
        """
        Create dump files in database using a bulk creation.

        NOTE: Remember that bulk discard the save() method.

        Arguments:
            files (list): List of DumpedFile objects for directory children files.
        """
        MediaFile.objects.bulk_create([
            MediaFile(**item.convert_to_orm_fields())
            for item in files
        ], batch_size=self.batch_limit)

    def edit_files(self, files):
        """
        Create dump files in database using a bulk creation.

        NOTE: Remember that bulk discard the save() method.

        NOTE: Performance could be better with a diff implementation to know the fields
        that have really changed and to avoid to always edit all allowed fields.
        Especially since the common updates will probably be on some few fields (like
        size or date).

        Arguments:
            files (list): List of DumpedFile objects for directory children files.
                Opposed to ``create_files``, the DumpedFile objects are expected to
                transport a MediaFile object which have been retrieved during
                distribution. This object will be used to proceed to bulk update.
        """
        bulk_items = []

        for item in files:
            #print(item._mediafile, type(item._mediafile))
            assert isinstance(item._mediafile, MediaFile) is True

            for name, value in item.convert_to_orm_fields().items():
                if name in self.EDITABLE_FIELDS:
                    setattr(item._mediafile, name, value)

        MediaFile.objects.bulk_update(bulk_items, self.EDITABLE_FIELDS)


    def store_files(self, dirname, dirdata):
        """
        TODO

        Arguments:
            directory (dict):

        Returns:
            foo:
        """
        print()
        print(dirname)
        print("="*len(dirname))

        for file_data in dirdata["children_files"]:
            print(file_data["path"])

            foo = {
                "path": file_data["path"],
                "absolute_dir": file_data["absolute_dir"],
                "directory": file_data["directory"],
                "filename": file_data["name"],
                "container": file_data["extension"],
                "filesize": file_data["size"],
                "stored_date": file_data["mtime"],
            }

            #mediafile = MediaFile(**serializer.data)
            #mediafile.full_clean()
            #mediafile.save()

        return

    def load(self, dump):
        """
        Arguments:
            dump (pathlib.Path): The path object for the dump file to load.
        """
        dump_content = self.open_dump(dump)

        for directory, data in dump_content.items():
            self.file_distribution(directory, data)
