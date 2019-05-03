#!/bin/bash

cd /app/gran_turismo/

python3 manage.py migrate
python3 manage.py collectstatic --no-input --clear
uwsgi --http :555 --module gran_turismo.wsgi
