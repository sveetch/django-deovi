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
        "BASE_DIR",
        "DEPLOYMENT_APPNAME",
        "DEPLOYMENT_BUILD_DESTINATION",
        "DEPLOYMENT_CONFIGURATIONS",
        "DEPLOYMENT_LOGS_DIRPATH",
        "DEPLOYMENT_HTTPSERVER_PORT",
        "DEPLOYMENT_USER",
        "DEPLOYMENT_GROUP",
    ]

    def add_arguments(self, parser):
        pass

    def get_context(self, extra=None):
        """
        Build template context.
        """
        context_data = {
            "settings_env": settings.SETTINGS_MODULE,
            # Include the whole setting object
            "settings": settings,
            # Additional computed variables
            "SOCKET_FILEPATH": settings.BASE_DIR / "run" / "gunicorn.sock",
            "APPSERVER_BINDING": None,
            "APPSERVER_BINDING_INTERFACE": None,
        }

        # Append search index alias if it exists
        context_data["SEARCH_INDEX"] = getattr(settings, "DEPLOYMENT_SEARCH_INDEX", None)

        appserver_binding = getattr(settings, "DEPLOYMENT_APPSERVER_BINDING", None)
        # As default without any binding we assume to use the socket
        if not appserver_binding:
            context_data["APPSERVER_BINDING"] = str(context_data["SOCKET_FILEPATH"])
            context_data["APPSERVER_BINDING_INTERFACE"] = "unix:" + str(
                context_data["SOCKET_FILEPATH"]
            )
        # When given binding value is a Path object we assume it is the socket filepath
        elif isinstance(appserver_binding, Path):
            context_data["SOCKET_FILEPATH"] = appserver_binding
            context_data["APPSERVER_BINDING"] = str(appserver_binding)
            context_data["APPSERVER_BINDING_INTERFACE"] = (
                "unix:" + str(appserver_binding)
            )
        # Finally any other given value is used as is. Commonly it is for a 'ip:port'
        # pattern. Socker filepath is emptied because it is useless.
        else:
            context_data["SOCKET_FILEPATH"] = None
            context_data["APPSERVER_BINDING"] = appserver_binding
            context_data["APPSERVER_BINDING_INTERFACE"] = appserver_binding

        if extra:
            context_data.update(extra)

        return context_data

    def get_configuration_payload(self, config):
        """
        Return a proper dictionnary for a given configuration item.

        A config item can be either a string or a dict. If it's a string it is
        assumed to be the template path to use and the other configuration data will be
        computed from.

        Returns:
            dict:
        """
        if not isinstance(config, str) and not isinstance(config, dict):
            raise CommandError(
                "A deployment configuration item can only be a string or a dictionnary."
            )

        payload = {
            "source": None,
            "destination": None,
            "chmod": None,
        }

        if isinstance(config, str):
            payload.update({"source": Path(config)})
        elif not config.get("source", None):
            raise CommandError("The 'source' item is mandatory.")
        else:
            payload.update(config)

        if not payload["destination"]:
            payload["destination"] = (
                settings.DEPLOYMENT_BUILD_DESTINATION / Path(payload["source"]).name
            )
        else:
            payload["destination"] = payload["destination"]

        return payload

    def build_configuration_file(self, configuration, context):
        """
        Render a configuration template with given context.
        """
        msg = "- Building configuration from template '{source}' to '{to}'."

        self.stdout.write(
            msg.format(source=configuration["source"], to=configuration["destination"])
        )
        appserver_template = get_template(configuration["source"])
        rendered_configuration = appserver_template.render(context)

        configuration["destination"].write_text(rendered_configuration)

        return configuration["destination"]

    def process_configurations(self):
        """
        Process all configuration templates rendering.
        """
        context = self.get_context()

        # Prebuild configuration before writting any files
        config_jobs = [
            self.get_configuration_payload(item)
            for item in settings.DEPLOYMENT_CONFIGURATIONS
        ]

        for config in config_jobs:
            # Create destination parent directory if it does not exist yet
            if not config["destination"].parent.exists():
                config["destination"].parent.mkdir()

            # Write configuration file in its destination
            written = self.build_configuration_file(config, context)

            # Apply chmod permission on file if given
            if config["chmod"]:
                written.chmod(config["chmod"])

        return config_jobs

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("👷 Starting 👷")
        )

        # Check for mandatory settings
        missing_settings = [
            item
            for item in self.MANDATORY_SETTINGS
            if not getattr(settings, item, None)
        ]

        if missing_settings:
            raise CommandError(
                "Settings are missing some mandatory setting names: {}".format(
                    ", ".join(missing_settings)
                )
            )

        # Start to process each defined configuration item
        self.process_configurations()
