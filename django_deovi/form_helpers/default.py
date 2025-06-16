from crispy_forms.helper import FormHelper


class DefaultFormHelper(FormHelper):
    """
    Default form layout helper with Crispy forms.

    Attributes starting with ``DEFAULT_`` are the default values for helper options.
    Use it only for hardcoded values and prefer to fill them in respective ``provide_``
    method for evaluated values (like Layout object, url resolving, queryset, etc..).
    """
    DEFAULT_ACTION = "."
    DEFAULT_ATTRS = {"novalidate": ""}
    DEFAULT_CSSCLASSES = "needs-validation"
    DEFAULT_CSSID = None
    DEFAULT_ENABLETAG = True
    DEFAULT_INPUTS = None
    DEFAULT_LAYOUT = None
    DEFAULT_METHOD = "post"

    def __init__(self, *args, **kwargs):
        self.provide_attrs(kwargs.pop("attrs", None))
        self.provide_action(kwargs.pop("action", None))
        self.provide_cssclass(kwargs.pop("cssclass", None))
        self.provide_cssid(kwargs.pop("cssid", None))
        self.provide_tag(kwargs.pop("tag", None))
        self.provide_method(kwargs.pop("method", None))
        self.provide_layout(
            kwargs.pop("layout", None),
            layout_args=kwargs.pop("layout_args", None),
            layout_kwargs=kwargs.pop("layout_kwargs", None)
        )
        self.provide_inputs(kwargs.pop("inputs", None))

        super().__init__(*args, **kwargs)

    def provide_action(self, value=None):
        value = value or self.DEFAULT_ACTION
        if value:
            self.form_action = value

    def provide_attrs(self, value=None):
        value = value or self.DEFAULT_ATTRS
        if value:
            self.form_attrs = value

    def provide_cssclass(self, value=None):
        value = value or self.DEFAULT_CSSCLASSES
        if value:
            self.form_class = value

    def provide_cssid(self, value=None):
        value = value or self.DEFAULT_CSSID
        if value:
            self.form_id = value

    def provide_tag(self, value=None):
        value = value or self.DEFAULT_ENABLETAG
        if value:
            self.form_tag = value

    def provide_method(self, value=None):
        value = value or self.DEFAULT_METHOD
        if value:
            self.form_method = value

    def provide_inputs(self, value=None):
        value = value or self.DEFAULT_INPUTS
        if value:
            self.form_method = value
            for item in value:
                self.add_input(item)

    def provide_layout(self, value=None, layout_args=None, layout_kwargs=None):
        value = value or self.DEFAULT_LAYOUT
        if value:
            self.layout = value
