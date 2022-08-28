from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from ...loader import DumpLoader
from ...models import MediaFile
from ...outputs import DjangoCommandOutput


class Command(BaseCommand):
    """
    Deovi dump loader
    """
    help = (
        "This should load a Deovi collection dump into database."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "source",
            type=Path,
            default=None,
            help="Path to the Deovi collection dump",
        )

    def collect_dump(self, filepath):
        """
        Load the dump contents into database.
        """
        self.stdout.write(
            self.style.SUCCESS("Opening dump: {}".format(filepath))
        )
        logger = DjangoCommandOutput(command=self)
        loader = DumpLoader(output_interface=logger)
        loader.load(filepath)

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("=== Starting loading dump ===")
        )

        if not options["source"].exists():
            msg = "Given source does not exists: {}".format(str(options["source"]))
            raise CommandError(msg)

        self.collect_dump(options["source"])
