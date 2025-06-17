import math

from django import template
from django.conf import settings

from ..forms import GlobalSearchForm
from ..utils.formatters import format_number as format_number_func

register = template.Library()


@register.filter("range")
def range_filter(end, start=0):
    """
    Filter to reproduce basic Python 'range()' function.

    Usage: ::

        {{ level|range:1 }}

    Arguments:
        value (integer): The value for range end.
        starts (string): The value to range start.

    Returns:
        list: List of range integers.
    """
    return list(range(start, end + 1))


@register.simple_tag
def format_number(value, precision=None, unit=None):
    """
    Format a given value (integer, float or string).

    Usage: ::

        {% format_number value %}
        {% format_number value precision="1.000" %}
        {% format_number value precision="1.000" unit="px" %}
    """
    options = {}

    if precision is not None:
        options["precision"] = precision

    if unit is not None:
        options["unit"] = unit

    return format_number_func(value, **options)


@register.simple_tag
def get_circle_values(value, radius=90):
    """
    Compute circle parameters from value (integer).

    Usage: ::

        {% get_circle_values value %}
        {% get_circle_values value radius="180" %}
    """
    circumference = (2 * math.pi) * radius
    offset = circumference * ((100 - value) / 100)

    return {
        "circumference": circumference,
        "offset": offset,
    }


@register.inclusion_tag(settings.DEOVI_SEARCH_TAG_TEMPLATE)
def minimal_search_form():
    """
    Display minimal search form.

    Usage: ::

        {% minimal_search_form %}
    """
    return {
        "minimal_search_form": GlobalSearchForm(minimal=True),
    }


@register.inclusion_tag(settings.DEVICE_OCCUPANCY_SVG)
def show_occupancy_svg(device, resume=None):
    """
    Render occupancy SVG for given device and its resume.

    If resume is not given, its method will be called from device object. Commonly in
    templates the resume as been memorized with ``{% with ... %}`` so it is more
    efficient to use it instead of calling again the method.

    Usage: ::

        {% show_occupancy_svg device %}
        {% show_occupancy_svg device resume=resume %}
    """
    return {
        "device": device,
        "resume": resume or device.resume(),
    }
