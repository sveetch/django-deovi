from django.conf import settings

from haystack.fields import (
    CharField as OriginalCharField,
    EdgeNgramField as OriginalEdgeNgramField
)


class DebuggingField:
    """
    A custom search field for CharField which is able to print the rendered indexes
    content when it is allowed so from ``settings.DEOVI_INDEXES_DEBUG``.
    """

    def prepare_template(self, obj):
        """
        Flattens an object for indexing.

        This loads a template
        (``search/indexes/{app_label}/{model_name}_{field_name}.txt``) and
        returns the result of rendering that template. ``object`` will be in
        its context.
        """
        if not settings.DEOVI_INDEXES_DEBUG:
            return super().prepare_template(obj)
        else:
            rendered = super().prepare_template(obj)
            title = "_____ <{}:{}> ".format(obj._meta.model.__name__, str(obj.id))
            print(title + ("_" * (60 - len(title))))
            print(rendered)
            return rendered


class CharField(DebuggingField, OriginalCharField):
    """
    A custom search field for CharField which is able to print the rendered indexes
    content when it is allowed so from ``settings.DEOVI_INDEXES_DEBUG``.
    """
    pass


class EdgeNgramField(DebuggingField, OriginalEdgeNgramField):
    """
    A custom search field for EdgeNgramField which is able to print the rendered indexes
    content when it is allowed so from ``settings.DEOVI_INDEXES_DEBUG``.
    """
    pass
