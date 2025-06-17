from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from crispy_forms.layout import Field, Layout
from crispy_forms.bootstrap import FieldWithButtons, StrictButton

from .default import DefaultFormHelper
from .layout_objects import ListGroupCheckboxes


class AdvancedSearchFormHelper(DefaultFormHelper):
    """
    Advanced search form layout helper contains every available search fields.
    """
    DEFAULT_CSSID = "advanced-search"
    DEFAULT_METHOD = "get"
    DEFAULT_CSSCLASSES = "search-advanced-form needs-validation"

    def __init__(self, *args, **kwargs):
        self.empty_query = kwargs.pop("empty_query", False)
        self.empty_models = kwargs.pop("empty_models", False)
        super().__init__(*args, **kwargs)

    def provide_action(self, value=None):
        self.form_action = reverse("django_deovi:search-results")

    def provide_layout(self, value=None, layout_args=None, layout_kwargs=None):
        query_extras = {} if not self.empty_query else {"autofocus": ""}
        models_extras = {} if not self.empty_models else {"checked": ""}

        self.layout = Layout(
            FieldWithButtons(
                Field("q", placeholder=_("Search"), required="", **query_extras),
                StrictButton("Go!", type="submit", css_class="btn-primary"),
                input_size="input-group-sm"
            ),
            ListGroupCheckboxes(
                "models",
                group_class="list-group-horizontal-md",
                item_class="list-group-item-light",
                **models_extras
            ),
        )


class MinimalSearchFormHelper(DefaultFormHelper):
    """
    Minimal search form layout helper contains only query input.
    """
    DEFAULT_CSSID = "minimal-search"
    DEFAULT_METHOD = "get"
    DEFAULT_CSSCLASSES = "search-minimal-form needs-validation"

    def provide_action(self, value=None):
        self.form_action = reverse("django_deovi:search-results")

    def provide_layout(self, value=None, layout_args=None, layout_kwargs=None):
        self.layout = Layout(
            FieldWithButtons(
                Field("q", placeholder=_("Search"), required=""),
                StrictButton("Go!", type="submit", css_class="btn-primary"),
                input_size="input-group-sm"
            ),
        )
