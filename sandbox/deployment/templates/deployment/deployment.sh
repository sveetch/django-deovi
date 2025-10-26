#!/bin/bash
# Script to deploy all configurations and start server components.
# The server is managed as a service from SystemV, it should be persistent
# after reboot.
{% include "deployment/_base_shell_context.sh" %}

echo "🔨 Preventive stop of existing service"
sudo systemctl stop $GUNICORN_SOCKET_FILENAME
sudo systemctl disable $GUNICORN_SOCKET_FILENAME

echo "🔧 Deploying Gunicorn service socket"
sudo rm -f /etc/systemd/system/$GUNICORN_SOCKET_FILENAME
sudo cp $DEPLOY_BUILDDIR/$GUNICORN_SOCKET_FILENAME /etc/systemd/system/
sudo systemctl restart $GUNICORN_SOCKET_FILENAME
sudo systemctl enable $GUNICORN_SOCKET_FILENAME

echo "🔧 Deploying Gunicorn service descriptor"
sudo rm -f /etc/systemd/system/$GUNICORN_SERVICE_FILENAME
sudo cp $DEPLOY_BUILDDIR/$GUNICORN_SERVICE_FILENAME /etc/systemd/system/
sudo systemctl daemon-reload

echo "🏗️Preparing static files"
$MANAGE_SCRIPT collectstatic --settings $SETTINGS_MODULE;
mkdir -p $STATICDIR
chmod -R 0755 $STATICDIR
chown -R $DEPLOY_USER:$DEPLOY_USER $STATICDIR

echo "🏗️Preparing media files"
mkdir -p $MEDIADIR
chmod -R 0755 $MEDIADIR
chown -R $DEPLOY_USER:$DEPLOY_USER $MEDIADIR

echo "🏗️Preparing search index"
mkdir -p $SEARCH_INDEX
chmod -R 0755 $SEARCH_INDEX
chown -R $DEPLOY_USER:$DEPLOY_USER $SEARCH_INDEX

echo "🔧 Deploying Nginx site configuration"
sudo cp $DEPLOY_BUILDDIR/$NGINX_CONFIG_FILENAME /etc/nginx/sites-available/
sudo rm -f /etc/nginx/sites-enabled/$NGINX_CONFIG_FILENAME
sudo ln -s /etc/nginx/sites-available/$NGINX_CONFIG_FILENAME /etc/nginx/sites-enabled/
sudo systemctl reload nginx
