from crispy_forms.layout import Field
from crispy_forms.utils import TEMPLATE_PACK


class ListGroupCheckboxes(Field):
    """
    Layout object for rendering checkboxes in a *List group*.

    Opposed to other crispy layout fields this one do not include content into a wrapper
    'div' but in the 'ul' group. So its ``wrapper_class`` and ``css_class`` arguments
    are useless.

    Example:

        ListGroupCheckboxes("field_name", group_class="")

    Arguments:
        **kwargs: Additional attributes are converted into key="value", pairs. These
            attributes are added to the ``<ul>``.

    Keyword Arguments:
        group_class (string): CSS class to apply on ``<ul>`` group.
        item_class (string): CSS class to apply on all ``<li>`` items.
    """

    template = "%s/layout/listgroupcheckboxes.html"

    def __init__(self, *args, **kwargs):
        self.group_class = kwargs.pop("group_class", None)
        self.item_class = kwargs.pop("item_class", None)

        super().__init__(*args, **kwargs)

    def render(self, form, context, template_pack=TEMPLATE_PACK, **kwargs):
        return super().render(
            form,
            context,
            template_pack=template_pack,
            extra_context={
                "group_class": self.group_class,
                "item_class": self.item_class,
            },
        )
