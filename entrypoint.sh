#!/bin/bash

python3 /app/context_proxy.py
cp /app/config.cfg /etc/nginx/sites-enabled/default
service nginx restart