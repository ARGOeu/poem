import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Poem.settings')
django.setup()

import string
import sys
import urllib.request
import logging
import Poem.django_logging
from Poem import settings
from Poem.poem import models
from Poem.tenants.models import Tenant
from django.db import connection
from xml.etree import ElementTree
from tenant_schemas.utils import schema_context, get_public_schema_name
from configparser import ConfigParser

logging.basicConfig(format='%(filename)s[%(process)s]: %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger("POEM")


def tenant_vo_url(tenant):
    config = ConfigParser()
    config.read(settings.CONFIG_FILE)

    return config.get('SYNC_' + tenant.upper(), 'vo')


def main():
    "Parses VO list provided by CIC portal"

    schemas = list(Tenant.objects.all().values_list('schema_name', flat=True))
    schemas.remove(get_public_schema_name())

    for schema in schemas:
        with schema_context(schema):
            tenant = Tenant.objects.get(schema_name=schema)

            try:
                ret = urllib.request.urlopen(tenant_vo_url(tenant.name),
                                             timeout=60).read()
            except Exception as e:
                logger.error('VO card - '+'%s' % (e))
                sys.exit(1)
            try:
                Root = ElementTree.XML(ret)
                idcards = Root.findall("IDCard")
            except Exception as e:
                logger.error('Could not parse VO card - '+'%s' % (e))
                sys.exit(1)
            if len(idcards) > 0:
                vos = []
                for vo_element in idcards:
                    dict_vo_element = dict(vo_element.items())
                    if 'Name' not in dict_vo_element or 'Status' not in dict_vo_element:
                        logger.warning("vo card does not contain 'Name' and 'Status' attributes for %s" % vo_element)
                    else:
                        if dict_vo_element['Status'].lower() == 'production' and dict_vo_element['Name'] != '':
                            vos.append(dict_vo_element['Name'])
            else:
                logger.error("Error synchronizing VO due to invalid VO card")
                sys.exit(1)

            voindb = set([(vo.name,) for vo in models.VO.objects.all()])
            if len(voindb) != len(vos):
                svos = set([(vo,) for vo in vos])
                cur = connection.cursor()
                if len(voindb) < len(vos):
                    cur.executemany('INSERT INTO poem_vo VALUES (?)', svos.difference(voindb))
                    logger.info("Added %d VO" %\
                                (len(vos) - len(voindb)))
                elif len(voindb) > len(vos):
                    cur.executemany('DELETE FROM poem_vo WHERE name IN (?)', voindb.difference(svos))
                    logger.info("Deleted %d VO" %\
                                (len(voindb) - len(vos)))
                connection.close()
            else:
                logger.info("VO database is up to date")

main()
