from dataclasses import dataclass


@dataclass
class DumpedFile:
    """
    This is a basic NON Django model object.

    This use the Python dataclass to automatically implement comparaison as we could
    expect from a proper data object.

    Arguments:
        **kwargs: Items to set field attributes. Only allowed field names from
            ``DumpedFile.FIELDNAMES`` are set as object attribute.

    Keyword Arguments:
        mediafile (django_deovi.models.MediaFile): A MediaFile object to transport in
            ``_mediafile`` attribute.

    Attributes:
        _mediafile (django_deovi.models.MediaFile): A convenience to transport related
            MediaFile object if given in keyword argument ``mediafile``. There won't
            be any operations on this attribute and it will never be dumped from
            serialization.

    """
    # List of name to set as attributes from given kwargs, all of them are required
    FIELDNAMES = [
        "path", "name", "absolute_dir", "relative_dir", "directory", "extension",
        "container", "size", "mtime"
    ]
    # Associations of "DumpedFile fieldname : MediaFile fieldname"
    MEDIA_FILES_FIELDS = {
        "path": "path",
        "name": "filename",
        "absolute_dir": "absolute_dir",
        "directory": "directory",
        "extension": "container",
        "size": "filesize",
        "mtime": "stored_date",
    }

    def __init__(self, *args, **kwargs):
        self._mediafile = kwargs.pop("mediafile", None)

        for item in self.FIELDNAMES:
            # TODO: Every fields should required, despite there are kwargs
            setattr(self, item, kwargs.get(item))

    def __repr__(self):
        return "<DumpedFile: {}>".format(self.path)

    def __str__(self):
        return self.path

    def __getitem__(self, item):
        """
        Make it so the object is subscriptable but only with getter, not setter.

        This is not really safe but the DumpedFile is a pretty simple and naive object
        so don't bother.
        """
        return getattr(self, item)

    @classmethod
    def from_dict(cls, **kwargs):
        """
        Static method to return a DumpedFile created from given payload dict

        NOTE: It does not seems more useful than to use directly "DumpedFile(**kwargs)"
        """
        return cls(**kwargs)

    def to_dict(self):
        """
        Returns instance values as a dictionnary
        """
        return {
            item: getattr(self, item)
            for item in self.FIELDNAMES
        }

    def convert_to_orm_fields(self):
        """
        Return a dictionnary of fields but with the MediaFile field names.
        """
        return {
            modelname: getattr(self, dumpname)
            for dumpname, modelname in self.MEDIA_FILES_FIELDS.items()
        }
