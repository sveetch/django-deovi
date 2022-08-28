# -*- coding: utf-8 -*-
"""
Exceptions
==========

Specific application exceptions.
"""


class DjangoDeoviBaseException(Exception):
    """
    Exception base.

    You should never use it directly except for test purpose. Instead make or
    use a dedicated exception related to the error context.
    """
    pass


class DjangoDeoviError(DjangoDeoviBaseException):
    """
    Common basic error.
    """
    pass
