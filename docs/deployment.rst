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


Introduction
************

We will deploy this project with:

Gunicorn
    The Application server using Web Server Gateway Interface (WSGI).

    It will be installed from included project deployment requirements.

Nginx
    * As the web server mainly to serve static files;
    * And as reverse proxy to pipe to the Application server;

    You will have to install it yourself on your system, on some distribution like
    Ubuntu it is commonly already installed.

Systemd services
    Possibly to manage the Gunicorn socket as a service (so it can be automatically
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


Further things to concern
*************************

* Whitenoise
* `django-downloadview <https://github.com/jazzband/django-downloadview>`_;
* `uvicorn-worker <https://github.com/Kludex/uvicorn-worker>`_ to implement ASGI within Gunicorn;


Another deployment helpers for Django
*************************************

* https://github.com/django-simple-deploy/django-simple-deploy
* https://github.com/jdbit/django-auto-deploy
* https://github.com/octue/django-gcp
