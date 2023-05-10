#!/bin/bash

python manage.py migrate --noinput && \
python manage.py loaddata groups.json && \
python manage.py createsuperuser --noinput && \
python manage.py runserver 0.0.0.0:8000