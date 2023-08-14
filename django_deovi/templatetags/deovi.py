from django import template

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
