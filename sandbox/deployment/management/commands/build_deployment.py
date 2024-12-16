from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import get_template


class Command(BaseCommand):
    """
    Deployment configurations builder.

    * The full setting attributes are exposed to the configuration templates.
    * Configuration files are always written into the same config dir
    * Configuration file name will use the base template name (without path dirs)

    Attributes:
        MANDATORY_SETTINGS (list): A list of setting names that are required.
    """
    help = (
        "Build configuration files for deployment."
    )
    MANDATORY_SETTINGS = [
        "DEPLOYMENT_APPNAME",
        "DEPLOYMENT_BUILD_DESTINATION",
        "DEPLOYMENT_CONFIGURATIONS",
    ]

    def add_arguments(self, parser):
        pass

    def get_context(self, extra=None):
        """
        Build template context.
        """
        context_data = {
            "settings_env": settings.SETTINGS_MODULE,
            "settings": settings,
        }

        if extra:
            context_data.update(extra)

        return context_data

    def get_configuration(self, config):
        """
        Return a proper dictionnary for a given configuration item.

        A config item can be either a string or a dict. If it's a string it will be
        turned to a dict.
        """
        data = {
            "source": None,
            "chmod": None,
        }

        if isinstance(config, str):
            config = {"source": config}
        elif not isinstance(config, dict):
            raise CommandError(
                "A deployment configuration item can only be a string or a dictionnary."
            )

        data.update(config)

        return data

    def build_configuration(self, template_path, context):
        """
        Render a configuration template with given context.
        """
        msg = "- Building configuration from template '{source}' to '{to}'."
        destination = (
            settings.DEPLOYMENT_BUILD_DESTINATION / Path(template_path).name
        )
        self.stdout.write(msg.format(source=template_path, to=destination))
        appserver_template = get_template(template_path)
        rendered_configuration = appserver_template.render(context)

        destination.write_text(rendered_configuration)

        return destination

    def process_configurations(self):
        """
        Process all configuration templates rendering.
        """
        context = self.get_context()

        for item in settings.DEPLOYMENT_CONFIGURATIONS:
            config = self.get_configuration(item)
            written = self.build_configuration(config["source"], context)
            if config["chmod"]:
                written.chmod(config["chmod"])

        return

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("=== Starting ===")
        )

        missing_settings = [
            item
            for item in self.MANDATORY_SETTINGS
            if not hasattr(settings, item)
        ]

        if missing_settings:
            raise CommandError(
                "Settings are missing some mandatory setting names: {}".format(
                    ", ".join(missing_settings)
                )
            )

        # Create destination directory
        if not settings.DEPLOYMENT_BUILD_DESTINATION.exists():
            settings.DEPLOYMENT_BUILD_DESTINATION.mkdir()

        self.process_configurations()
