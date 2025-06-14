"""
Django settings for deployment
"""
from .base import *  # noqa: F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": VAR_PATH / "db" / "production.sqlite3",  # noqa: F405
    }
}

TIME_ZONE = "Europe/Paris"

INSTALLED_APPS.append("deployment")

# Name used for Gunicorn process and Nginx internal host
# No special characters here, only alphabet, digits and underscore character.
# Everything else is subject to cause issue
DEPLOYMENT_APPNAME = "django_deovi"

# Where to build all the configuration files
DEPLOYMENT_BUILD_DESTINATION = BASE_DIR / "etc"

# Where server will write logging files
DEPLOYMENT_LOGS_DIRPATH = VAR_PATH / "logs"

# List of configuration template to render with possible options
DEPLOYMENT_CONFIGURATIONS = (
    "deployment/nginx.conf",
    {"source": "deployment/gunicorn_start", "chmod": 0o755},
)

# The host port which be listened by the web server to respond to requests
DEPLOYMENT_WEBSERVER_PORT = 8101

# Import local settings if any
try:
    from .local import *  # noqa: F401,F403
except ImportError:
    pass
