"""
Django settings for production

.. Hint::
    Basically the production environment should not share database and media files with
    the non-production environments.
"""
from .base import *  # noqa: F403

#
# Adjust ressources and config to the production environment
#
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": VAR_PATH / "db" / "production.sqlite3",  # noqa: F405
    }
}

TIME_ZONE = "Europe/Paris"
LANGUAGE_CODE = "fr"

MEDIA_ROOT = VAR_PATH / "media-production"

STATIC_ROOT = VAR_PATH / "static-production"

HAYSTACK_CONNECTIONS["default"]["PATH"] = VAR_PATH / "whoosh_index-production"

#
# Settings for the internal app 'deployment'
#

INSTALLED_APPS.append("sandbox.deployment")

# Shortcut alias to the search index backend file
DEPLOYMENT_SEARCH_INDEX = HAYSTACK_CONNECTIONS["default"]["PATH"]

# Name used for Gunicorn process and Nginx internal host
# No special characters here, only alphabet, digits and underscore character.
# Everything else is subject to cause issues.
DEPLOYMENT_APPNAME = "django_deovi"

# Where to build all the configuration files
DEPLOYMENT_BUILD_DESTINATION = BASE_DIR / "etc"

# Where server will write logging files
DEPLOYMENT_LOGS_DIRPATH = VAR_PATH / "logs"

# The host port which be listened by the web server to respond to requests
DEPLOYMENT_HTTPSERVER_PORT = 8101

# The system user and group that will run the service
DEPLOYMENT_USER = "emencia"
DEPLOYMENT_GROUP = "www-data"

# List of configuration template to render with possible options
DEPLOYMENT_CONFIGURATIONS = (
    "deployment/settings.json",
    {
        "source": "deployment/nginx.conf",
        "chmod": 0o644,
        "destination": DEPLOYMENT_BUILD_DESTINATION / ("010_" + DEPLOYMENT_APPNAME),
    },
    {
        "source": "deployment/gunicorn_start",
        "chmod": 0o755,
        "destination": DEPLOYMENT_BUILD_DESTINATION / "gunicorn_launcher.sh",
    },
    {
        "source": "deployment/gunicorn.socket",
        "chmod": 0o644,
        "destination": DEPLOYMENT_BUILD_DESTINATION / ("gunicorn_" + DEPLOYMENT_APPNAME + ".socket")
    },
    {
        "source": "deployment/gunicorn.service",
        "chmod": 0o644,
        "destination": DEPLOYMENT_BUILD_DESTINATION / ("gunicorn_" + DEPLOYMENT_APPNAME + ".service")
    },
    {
        "source": "deployment/deployment.sh",
        "chmod": 0o755,
        "destination": DEPLOYMENT_BUILD_DESTINATION / "deploy.sh",
    },
    {
        "source": "deployment/cleaning.sh",
        "chmod": 0o755,
        "destination": DEPLOYMENT_BUILD_DESTINATION / "clean.sh",
    },
)

# The interface to bind gunicorn on. It may be either a socket or adress IP with a port.
# As default (empty or not set) it will be a socket into 'run/' dir created at project
# base dir
# DEPLOYMENT_APPSERVER_BINDING = None
# IP address with a port, not efficient but may be useful to debug. SystemV service
# may not work well with an IP
# DEPLOYMENT_APPSERVER_BINDING = "0.0.0.0:8080"
# Path object for the socket directory
DEPLOYMENT_APPSERVER_BINDING = Path("/run/gunicorn_" + DEPLOYMENT_APPNAME + ".sock")

# Import local settings if any
try:
    from .local import *  # noqa: F401,F403
except ImportError:
    pass
