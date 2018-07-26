#!/bin/bash

# load virtual environment
source /etc/profile.d/venv_poem.sh
workon poem

# prerequisites
poem-genseckey -f $WORKON_HOME/poem/etc/poem/secret_key
cp -f poem.conf $WORKON_HOME/poem/etc/poem/poem.conf
chown -R apache:apache $WORKON_HOME
poem-db -c
ln -f -s $WORKON_HOME/poem/etc/httpd/conf.d/poem.conf /etc/httpd/conf.d/
ln -f -s $WORKON_HOME/poem/etc/cron.d/poem-clearsessions /etc/cron.d/
ln -f -s $WORKON_HOME/poem/etc/cron.d/poem-syncvosf /etc/cron.d/
