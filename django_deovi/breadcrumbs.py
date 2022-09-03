"""
This is just a shortand to safely import the breadcrumb view mixin if it is correctly
installed.
"""

try:
    from view_breadcrumbs import BaseBreadcrumbMixin
except ImportError:
    from .mixins import NoOperationBreadcrumMixin as BaseBreadcrumbMixin
