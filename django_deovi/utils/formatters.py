from decimal import Decimal


def format_number(value, precision="1.00", unit=None):
    """
    Format given number value with float precision using Decimal.

    Arguments:
        value (integer or float or string): The number value to format.

    Keyword Arguments:
        precision (string): Precision pattern to use. On default this will format
            value with exactly two decimals.
        unit (string): Optional unit text to append after formatted value. On default
            there is no unit.

    Returns:
        string: Formatted value.
    """
    value = Decimal(value).quantize(Decimal(precision))

    if unit:
        return str(value) + unit

    return value
