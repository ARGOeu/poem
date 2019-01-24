import os
import django
import logging
import requests
import json
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Poem.settings')
django.setup()

from Poem.poem.models import Service
from Poem import settings


logging.basicConfig(format='%(filename)s[%(process)s]: %(levelname)s %('
                           'message)s', level=logging.INFO)
logger = logging.getLogger('POEM')


def main():
    """Parses service areas, services and service types from eosc-hub api."""
    try:
        r = requests.get(settings.SERVICE_URL)
    except Exception as e:
        logger.error('Request - %s' % repr(e))
        sys.exit(1)
    try:
        feed = json.loads(r.text)
    except json.JSONDecodeError:
        logger.error('Decoding JSON has failed.')
        sys.exit(1)
    dummy_uptodate = 0
    dummy_added = 0
    dummy_deleted = 0
    dummy_changed = 0

    for data in feed:
        db_entry = Service.objects.filter(id=data['id']).values()
        if db_entry:
            if [db for db in db_entry][0] == data:
                dummy_uptodate += 1
            else:
                db_entry = Service(**data)
                db_entry.save()
                dummy_changed += 1
        else:
            try:
                Service.objects.create(**data)
                dummy_added += 1
            except Exception as e:
                logger.error('Could not save data to database - %s' % repr(e))
                sys.exit(1)

    service_entry_in_db = [serv.id for serv in Service.objects.all()]
    if len(service_entry_in_db) > len(feed):
        for sid in service_entry_in_db:
            if sid not in [data['id'] for data in feed]:
                Service.objects.filter(id=sid).delete()
                dummy_deleted += 1

    if dummy_added != 0:
        logger.info('Added %d Service entries.' % dummy_added)

    if dummy_deleted != 0:
        logger.info('Deleted %d Service entries.' % dummy_deleted)

    if dummy_changed != 0:
        logger.info('Updated %d Service entries.' % dummy_changed)

    if dummy_uptodate > 0 and dummy_changed == 0 and dummy_deleted == 0 and \
            dummy_added == 0:
        logger.info('Service database is up-to-date.')


main()
