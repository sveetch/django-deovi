#!/bin/bash
# Script to clean configurations and crumbs
{% include "deployment/_base_shell_context.sh" %}

echo "🔨 Preventive stop of existing service"
sudo systemctl stop $GUNICORN_SOCKET_FILENAME
sudo systemctl disable $GUNICORN_SOCKET_FILENAME

echo "🗑️Removing service descriptor"
sudo rm -f /etc/systemd/system/$GUNICORN_SOCKET_FILENAME

echo "🗑️Removing service socket"
sudo rm -f /etc/systemd/system/$GUNICORN_SERVICE_FILENAME

echo "💫 Reload SystemV"
sudo systemctl daemon-reload
sudo systemctl reset-failed $GUNICORN_SOCKET_FILENAME

echo "🗑️Removing Gunicorn sock file from '/run/'"
sudo rm -f $DEPLOY_SOCKET_FILEPATH

echo "🗑️Removing Nginx config"
sudo rm -f /etc/nginx/sites-enabled/$NGINX_CONFIG_FILENAME
sudo rm -f /etc/nginx/sites-available/$NGINX_CONFIG_FILENAME

echo "💫 Reload Nginx"
sudo systemctl reload nginx
