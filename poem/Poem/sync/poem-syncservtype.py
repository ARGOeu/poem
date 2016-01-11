#!/usr/bin/python

import string
import sys
import urllib2
import httplib
import os
import logging
import Poem.django_logging
from Poem import settings
from Poem.poem import models
from django.db import connection, transaction
from xml.etree import ElementTree
from urlparse import urlparse

logging.basicConfig(format='%(filename)s[%(process)s]: %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger("POEM")

def main():
    "Parses service flavours list from GOCDB"

    Feed_List = None
    fos = []

    try:
        for fp in [settings.HOST_CERT, settings.HOST_KEY]:
            if not os.path.exists(fp):
                raise IOError("invalid path %s" % (fp))
            else:
                fos.append(open(fp))
    except IOError as e:
        logger.error(e)
        raise SystemExit(1)
    for fo in fos:
        fo.close()

    o = urlparse(settings.GOCDB_SERVICETYPE_URL)
    try:
        if o.scheme.startswith('https'):
            conn = httplib.HTTPSConnection(host=o.netloc, \
                                            key_file=settings.HOST_KEY, cert_file=settings.HOST_CERT)
        else:
            conn = httplib.HTTPSConnection(host=o.netloc)
        conn.putrequest('GET', o.path+'?'+o.query)
        conn.endheaders()
        ret = conn.getresponse().read()
    except Exception as e:
        logger.error("Error service flavours feed - %s" % (e))
        raise SystemExit(1)

    try:
        Root = ElementTree.XML(ret)
    except Exception as e:
        logger.error("Error parsing service flavours - %s" % (e))
        raise SystemExit(1)

    elements = Root.findall("SERVICE_TYPE")
    if not elements:
        logger.error("Error parsing service flavours")
        raise SystemExit(1)

    Feed_List = []
    for element in elements:
        Element_List = {}
        if element.getchildren():
            for child_element in element.getchildren():
                Element_List[string.lower(child_element.tag)] = (child_element.text)
        Feed_List.append(Element_List)


    sfindb = set([(sf.name, sf.description) for sf in models.ServiceFlavour.objects.all()])
    if len(sfindb) != len(Feed_List) + 1:
        sfs = set([(feed['service_type_name'], feed['service_type_desc']) \
                for feed in Feed_List])
        sfs.add(('SRMv2', '[Site service] Storage Resource Manager. Mandatory for all sites running an SRM enabled storage element.'))
        cur = connection.cursor()
        try:
            if len(sfindb) < len(Feed_List) + 1:
                cur.executemany('INSERT INTO poem_serviceflavour VALUES (?,?)', \
                        sfs.difference(sfindb))
                logger.info("Added %d service flavours" %\
                            (len(Feed_List) + 1 - len(sfindb)))
            elif len(sfindb) > len(Feed_List) + 1:
                cur.executemany('DELETE FROM poem_serviceflavour WHERE name IN (?,?)', \
                        sfindb.difference(sfs))
                logger.info("Deleted %d service flavours" %\
                            (len(sfindb) - len(Feed_List) + 1))
            transaction.commit_unless_managed()
            connection.close()
        except Exception as e:
            logger.error("database operations failed - %s" % e)
    else:
        logger.info("Service Flavours database is up to date")

main()
