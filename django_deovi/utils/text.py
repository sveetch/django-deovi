import unicodedata


def normalize_text(value):
    """
    Common way to replace accent characters with their normal form.

    In short this would transform ``Élà plôp.`` to ``Ela plop.``

    Arguments:
        value (string): Text to normalize.

    Returns:
        string: Normalized text.
    """
    return (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
