.. _intro_install:

=======
Install
=======

Install package in your environment : ::

    pip install django-deovi

For development usage see :ref:`install_development`.

Configuration
*************

Add it to your installed Django apps in settings : ::

    INSTALLED_APPS = (
        ...
        "rest_framework",
        "django_deovi",
    )

Then load default application settings in your settings file: ::

    from django_deovi.settings import *

Then mount applications URLs: ::

    urlpatterns = [
        ...
        path("", include("django_deovi.urls")),
    ]

And finally apply database migrations.

Settings
********

.. automodule:: django_deovi.settings
   :members:
