from haystack.forms import ModelSearchForm

from ..models import Directory, MediaFile
from ..form_helpers import AdvancedSearchFormHelper, MinimalSearchFormHelper
from ..utils.text import normalize_text


class GlobalSearchForm(ModelSearchForm):
    """
    Form to search on all enabled Django Deovi models.
    """

    def __init__(self, *args, **kwargs):
        minimal_form = kwargs.pop("minimal", False)
        empty_query = kwargs.pop("empty_query", False)
        empty_models = kwargs.pop("empty_models", False)

        super().__init__(*args, **kwargs)

        # We don't want label since we use a group inline layout
        self.fields["q"].label = False
        self.fields["models"].label = False

        if not minimal_form:
            self.helper = AdvancedSearchFormHelper(
                empty_query=empty_query,
                empty_models=empty_models,
            )
        else:
            self.helper = MinimalSearchFormHelper()

    def search(self):
        """
        We don't keep the base queryset from inherit ModelSearchForm since it starts
        with an 'auto_query' that is not efficient with partial search. However this
        drops the feature of some operator like ``-`` to negate keywords.
        """
        if not self.is_valid():
            return self.no_query_found()

        if not self.cleaned_data.get("q"):
            return self.no_query_found()

        # Search on main content with normalized query
        sqs = self.searchqueryset.filter(text=normalize_text(self.cleaned_data["q"]))

        # Enable all discovered model indexes from enabled applications
        sqs = sqs.models(*self.get_models())

        if self.load_all:
            # Get model objects from search result references
            sqs = sqs.load_all()

            # Define Directory relationships to select in queryset instead of getting
            # them on their own querysets
            sqs = sqs.load_all_queryset(
                Directory,
                Directory.objects.all().select_related("device")
            )

            # Define MediaFile relationships to select
            sqs = sqs.load_all_queryset(
                MediaFile,
                MediaFile.objects.all().select_related("directory", "directory__device")
            )

        return sqs
