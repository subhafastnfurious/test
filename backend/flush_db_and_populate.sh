#!/bin/bash
set -ex

python manage.py reset_db --noinput
python manage.py migrate
python manage.py populate $@
