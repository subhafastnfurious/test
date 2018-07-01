FROM python:3.6.5
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client gettext zlib1g-dev
RUN mkdir -p /code/ /var/media /var/static
RUN chown -R 1000:2000 /var/media /var/static
RUN pip install uWSGI==2.0.17
WORKDIR /code/
COPY . /code/
RUN pip install -r /code/requirements.txt
EXPOSE 8000
ENV DJANGO_SETTINGS_MODULE=app.settings.production
COPY docker-entrypoint.sh /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD uwsgi \
    --harakiri=120 \
    --static-map /static=/var/static \
    --static-map /media/pictures=/var/media/pictures \
    --file /code/app/wsgi.py \
    --http-socket ":8000" \
    --workers 2 \
    --threads 8 \
    --uid 1000 \
    --gid 2000 \
    --buffer-size 16384
