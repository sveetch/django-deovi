import json

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from ...models import MediaFile
from ...serializers import MediaFileSerializer


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
        "Documentaires/La-guerre-des-trones": {
            "path": "/videos/Documentaires/La-guerre-des-trones",
            "name": "La-guerre-des-trones",
            "absolute_dir": "/videos/Documentaires",
            "relative_dir": "Documentaires/La-guerre-des-trones",
            "size": 4096,
            "mtime": "2022-06-13T02:32:50",
            "children_files": [
                {
                    "path": "/media/thenonda/OnoPrime/Loki/Loki.S01E01.mkv",
                    "name": "Loki.S01E01.mkv",
                    "absolute_dir": "/media/thenonda/OnoPrime/Loki",
                    "relative_dir": "Loki",
                    "directory": "Loki",
                    "extension": "mkv",
                    "container": "Matroska",
                    "size": 2299625319,
                    "mtime": "2021-10-22T01:29:05"
                },
            ],
        """
        self.stdout.write(
            self.style.SUCCESS("Opening dump: {}".format(filepath))
        )
        loader = DumpLoader()
        loader.load(filepath)


    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("=== Starting loading dump ===")
        )

        if not options["source"].exists():
            msg = "Given source does not exists: {}".format(str(options["source"]))
            raise CommandError(msg)

        self.collect_dump(options["source"])
