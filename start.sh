#!/usr/bin/env bash
nginx
celery worker -A app.celery &
uwsgi --ini app.ini