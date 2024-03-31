import datetime

from dataclasses import dataclass

from django.utils import timezone

from .exceptions import DjangoDeoviError


@dataclass
class DumpedFile:
    """
    This is a basic NON Django model object.

    DumpedFile is device agnostic.

    This use the Python dataclass to automatically implement comparaison as we could
    expect from a proper data object.

    Arguments:
        **kwargs: Items to set field attributes. Only allowed field names from
            ``DumpedFile.FIELDNAMES`` are set as object attribute. Every field value
            are expected to be strings except for the few integer like ``size``.

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
        "directory": "dirname",
        "extension": "container",
        "size": "filesize",
        "mtime": "stored_date",
    }

    def __init__(self, *args, **kwargs):
        self._mediafile = kwargs.pop("mediafile", None)
        self._set_fields(**kwargs)

    def _set_fields(self, **kwargs):
        """
        Set field attributes from given kwargs and then validate them if needed

        Arguments:
            **kwargs: Items to set field attributes. Only allowed field names from
                ``DumpedFile.FIELDNAMES`` are set as object attribute. Every field
                value is expected to be a string except for the few integer ones like
                ``size``.
        """
        _missing_kwargs = []

        for item in self.FIELDNAMES:
            if kwargs.get(item, None) is None:
                # Add field to the missing field list
                _missing_kwargs.append(item)
            else:
                # Validate some field value
                if item == "mtime" and not isinstance(kwargs.get(item), str):
                    msg = "DumpedFile.mtime must be a string in ISO format."
                    raise DjangoDeoviError(msg)

                setattr(self, item, kwargs.get(item))

        # If there is any missing required field, raise an error
        if _missing_kwargs:
            msg = "DumpedFile missed some required arguments: {}".format(
                ", ".join(_missing_kwargs)
            )
            raise DjangoDeoviError(msg)

    def __repr__(self):
        return "<DumpedFile: {}>".format(self.path)

    def __str__(self):
        return self.path

    def __getitem__(self, item):
        """
        This method ensure the object is subscriptable but only with getter, not
        setter.

        This is not really safe but the DumpedFile is a pretty simple and naive object
        so don't bother.

        Argument:
            item (string): The attribute name.

        Returns:
            object: The attribute value.
        """
        return getattr(self, item)

    @classmethod
    def from_dict(cls, **kwargs):
        """
        Static method to return a DumpedFile created from given payload dict

        Returns:
            DumpedFile: A DumpedFile object initialized with given kwargs.
        """
        return cls(**kwargs)

    def to_dict(self):
        """
        Returns instance values as a dictionnary

        Returns:
            dict: A dictionnary of attributes value for allowed field names.
        """
        return {
            item: getattr(self, item)
            for item in self.FIELDNAMES
        }

    def _convert_type(self, modelname, value):
        """
        Convert value type to the right one according to the field.

        stored_date
            If a string it will be converted to a datetime else it is assumed to
            already be a datetime object. Finally the returned datetime will be
            timezone aware, if the source already have it, it will stay unchanged else
            the default timezone (as from Django settings) will be added.

        Arguments:
            modelname (string): MediaFile model field name.
            value (object): The value to possibly convert to the right type.

        Returns:
            object: The value in the right type.
        """
        if modelname == "stored_date":
            parsed = datetime.datetime.fromisoformat(value)

            if timezone.is_naive(parsed):
                return parsed.replace(tzinfo=timezone.get_default_timezone())
            else:
                return parsed

        return value

    def convert_to_orm_fields(self):
        """
        Return a dictionnary of fields but with the MediaFile field names and value
        types.

        In fact the only re-typed value is the one from 'stored_date' which needs to
        be a datetime with timezone.
        """
        return {
            modelname: self._convert_type(modelname, getattr(self, dumpname))
            for dumpname, modelname in self.MEDIA_FILES_FIELDS.items()
        }
