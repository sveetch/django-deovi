"""
Django settings for demonstration

Intended to be used with ``make run``.
"""
from sandbox.settings.base import *  # noqa: F403

DEBUG = True

TEMPLATES[0]['OPTIONS']['debug'] = DEBUG  # noqa: F405

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": join(VAR_PATH, "db", "db.sqlite3"),  # noqa: F405
    }
}

TIME_ZONE = "Europe/Paris"

# Import local settings if any
try:
    from .local import *  # noqa: F401,F403
except ImportError:
    pass
