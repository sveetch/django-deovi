import string
import unicodedata


def normalize_text(value):
    """
    Common way to normalize a text to a alphanumeric version without any special
    characters.

    In short this would transform : ::

        Élà-plôp, lorem_ipsum.

    To: ::
        Ela plop lorem ipsum

    Arguments:
        value (string): Text to normalize.

    Returns:
        string: Normalized text.
    """
    # Replace all unicode character with its 'normalized' one and then replace every
    # punctuation character by a single whitespace
    cleaned = "".join([
        " " if v in string.punctuation else v
        for v in (
            unicodedata.normalize("NFKD", value).encode(
                "ascii",
                "ignore"
            ).decode("ascii")
        ).replace(",", "")
    ])
    # Finally ensure there are no useless whitespaces
    return " ".join(cleaned.split())
