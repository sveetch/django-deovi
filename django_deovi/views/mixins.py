try:
    from view_breadcrumbs import BaseBreadcrumbMixin
except ImportError:
    class BaseBreadcrumbMixin:
        """
        A dummy and empty mixin to use when 'django-view-breadcrumbs' is not available.
        """
        pass


class DeoviBreadcrumMixin(BaseBreadcrumbMixin):
    """
    A mixin to include base breadcrumb mixin if installed and some common
    breadcrumb options.
    """
    add_home = False
