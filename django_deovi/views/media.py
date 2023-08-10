from django.views.generic import DetailView


from ..models import MediaFile


class MediaFileDetailView(DetailView):
    """
    MediaFile detail
    """
    pk_url_kwarg = "mediafile_pk"
    template_name = "django_deovi/mediafile_detail.html"
    context_object_name = "mediafile_object"

    def get_queryset(self):
        """
        Get mediafile object, we validate it is related to required blog from
        query argument and set the blog object as an attribute for template
        context.
        """
        return MediaFile.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context["blog_object"] = self.blog_object

        return context
