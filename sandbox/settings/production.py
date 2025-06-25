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

#
# Settings for the internal app 'deployment'
#

INSTALLED_APPS.append("sandbox.deployment")

# Name used for Gunicorn process and Nginx internal host
# No special characters here, only alphabet, digits and underscore character.
# Everything else is subject to cause issue
DEPLOYMENT_APPNAME = "django_deovi"

# Where to build all the configuration files
DEPLOYMENT_BUILD_DESTINATION = BASE_DIR / "etc"

# Where server will write logging files
DEPLOYMENT_LOGS_DIRPATH = VAR_PATH / "logs"

# The host port which be listened by the web server to respond to requests
DEPLOYMENT_HTTPSERVER_PORT = 8101

# List of configuration template to render with possible options
DEPLOYMENT_CONFIGURATIONS = (
    "deployment/settings.json",
    {
        "source": "deployment/nginx.conf",
        "destination": DEPLOYMENT_BUILD_DESTINATION / "010_django_deovi",
    },
    {
        "source": "deployment/gunicorn_start",
        "chmod": 0o755,
        "destination": DEPLOYMENT_BUILD_DESTINATION / "gunicorn_launcher.sh",
    },
)

# The interface to bind gunicorn on. It may be either a socket or adress IP with a port.
# As default (empty or not set) it will be a socket into 'run/' dir created at project
# base dir
# DEPLOYMENT_APPSERVER_BINDING = None
# IP address with a port, not efficient but may be useful to debug
# DEPLOYMENT_APPSERVER_BINDING = "0.0.0.0:8080"
# Path object for the socket directory
DEPLOYMENT_APPSERVER_BINDING = BASE_DIR / "run" / "gunicorn.sock"

# Import local settings if any
try:
    from .local import *  # noqa: F401,F403
except ImportError:
    pass
