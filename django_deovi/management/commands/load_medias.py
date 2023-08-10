from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from ...loader import DumpLoader
from ...outputs import DjangoCommandOutput


class Command(BaseCommand):
    """
    Deovi dump loader
    """
    help = (
        "Load a Deovi device dump into database. Since file paths are unique, "
        "they are edited if they already exists in database. The other ones will be "
        "created."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "device",
            default=None,
            help=(
                "Device slug name to attach all collected directories from given "
                "dump. If the slug does not already exists it will be created, so be"
                "sure to use the exact slug to avoid importing stuff in a new device"
                "if you just planned to update things."
            ),
        )
        parser.add_argument(
            "source",
            type=Path,
            default=None,
            help="Path to the Deovi collection dump",
        )

    def collect_dump(self, device, filepath):
        """
        Load the dump contents into database.
        """
        self.stdout.write(
            self.style.SUCCESS("Opening dump: {}".format(filepath))
        )
        logger = DjangoCommandOutput(command=self)
        loader = DumpLoader(output_interface=logger)

        # Give the basepath computed from the dump path
        loader.load(device, filepath, covers_basepath=filepath.parent.resolve())

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("=== Starting loading dump ===")
        )

        if not options["source"].exists():
            msg = "Given dump path does not exists: {}".format(
                str(options["source"])
            )
            raise CommandError(msg)

        self.collect_dump(options["device"], options["source"])
