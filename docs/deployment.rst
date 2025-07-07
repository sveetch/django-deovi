.. _virtualenv: https://virtualenv.pypa.io
.. _pip: https://pip.pypa.io

.. _intro_deployment:

==========
Deployment
==========

.. Warning::
    This is currently a draft document.

.. Note::
    This document is an opiniotated "how-to" deploy an instance of a Django server for
    django-deovi using its sandbox.

    There is many ways to deploy a Django projects and this document will care about
    only one.

    We started this helped from articles:

    * https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu#step-7-creating-systemd-socket-and-service-files-for-gunicorn
    * https://medium.com/@ganapriyakheersagar/hosting-django-application-with-nginx-and-gunicorn-in-production-99e64dc4345a
    * https://blog.devgenius.io/setting-up-django-with-nginx-gunicorn-on-ubuntu-20-04-77f7c3c715a
    * https://docs.gunicorn.org/en/latest/deploy.html

    But finally we mostly followed the first one as the reference.


Introduction
************

The application will be runned with:

Gunicorn
    The Application server using Web Server Gateway Interface (WSGI).

    It will be installed from included project deployment requirements.

    .. Hint::
        Once launched within a socket, the Gunicorn instance can be reached with
        curl: ::

            curl --unix-socket /run/socketfile.sock localhost

        This can be helpful to debug deployment on Gunicorn part.

        And then also see the logs: ::

            sudo journalctl -u gunicorn

Nginx
    * As the web server mainly to serve static files;
    * And as reverse proxy to pipe requests to the Application server;

    You will have to install it yourself on your system but on some distribution like
    Ubuntu it is commonly already installed.

Systemd services
    To manage the Gunicorn socket as a service (so it can be automatically
    started on system boot).

    Except for some specific distribution, Systemd is already part of your system.

.. Attention::
    To properly install deployment requirements you will need a C compiler and the
    Python development library (commonly named ``python-dev`` or ``python3-dev``).


Steps to do
***********

1. Install deployment requirements with ``make deploy``
   2. Build deployment configurations
   3. Place configurations
4. Run the things
5. ...
6. Profit!

Filesystem permissions
**********************

There is a lot of issues to happen with Filesystem permissions.

* With our SystemV and Gunicorn configurations the Gunicorn processes will be
  runned through the user and group configured in settings;
* Nginx is runned with ``www-data`` user and group ``www-data``;
* Almost all command executed in our deployment shellscript use ``sudo``, however
  we care to the right permissions when needed;

The first thing to care is to set the right user and group for Gunicorn in
production settings. If you installed the project with user ``foobar`` and group
``foobar``, then it is these ones to configure in settings.

Finally Nginx user ``www-data`` need must be in the group ``foobar`` else it
won't be able to read static files, even if they are set with permission ``0777``,
to the user ``www-data`` and group ``www-data``.

.. Notes::
Some Linux distribution use another user like ``nginx`` to run Nginx, in this
document replace ``www-data`` with the right Nginx user if it is your case.


Another deployment helpers for Django
*************************************

* https://github.com/django-simple-deploy/django-simple-deploy
* https://github.com/jdbit/django-auto-deploy
* https://github.com/octue/django-gcp
