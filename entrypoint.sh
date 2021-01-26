#!/bin/bash

python3 /app/context_proxy.py
cp /app/config.cfg /etc/nginx/sites-enabled/default
cp /app/index.html /var/www/html/index.nginx-debian.html
service nginx stop
/usr/sbin/nginx -g "daemon off;"
