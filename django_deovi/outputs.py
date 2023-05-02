import logging

from django.core.management.base import CommandError

from .exceptions import DjangoDeoviError
from . import __pkgname__


class BaseOutput:
    """
    Basic output interface which use Python logging module.

    Mostly used in tests.
    """
    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger(__pkgname__)

    def debug(self, msg):
        self.log.debug(msg)

    def info(self, msg):
        self.log.info(msg)

    def warning(self, msg):
        self.log.warning(msg)

    def error(self, msg):
        self.log.error(msg)

    def critical(self, msg):
        """
        Critical error is assumed to be a breaking event.
        """
        raise DjangoDeoviError(msg)


class DjangoCommandOutput:
    """
    Output interface which use the Django stdout and style interface.

    Keyword Arguments:
        command (django.core.management.base.BaseCommand): The Django command which
            have the ``stdout`` and ``style`` attributes. This is required.
    """
    def __init__(self, *args, **kwargs):
        self.command = kwargs.get("command")

    def debug(self, msg):
        self.command.stdout.write(msg)

    def info(self, msg):
        self.command.stdout.write(
            self.command.style.SUCCESS(msg)
        )

    def warning(self, msg):
        self.command.stdout.write(
            self.command.style.WARNING(msg)
        )

    def error(self, msg):
        self.command.stdout.write(
            self.command.style.ERROR(msg)
        )

    def critical(self, msg):
        """
        Critical error is assumed to be a breaking event.
        """
        raise CommandError(msg)
