#!/bin/bash

# load virtual environment
source /etc/profile.d/venv_poem.sh
workon poem

# prerequisites
poem-genseckey -f $VIRTUAL_ENV/etc/poem/secret_key
cp -f poem.conf $VIRTUAL_ENV/etc/poem/poem.conf
chown -R apache:apache $VIRTUAL_ENV
poem-db -c
ln -f -s $VIRTUAL_ENV/etc/httpd/conf.d/poem.conf /etc/httpd/conf.d/
ln -f -s $VIRTUAL_ENV/etc/cron.d/poem-clearsessions /etc/cron.d/
ln -f -s $VIRTUAL_ENV/etc/cron.d/poem-syncvosf /etc/cron.d/
