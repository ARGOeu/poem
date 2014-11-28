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

logger = logging.getLogger("POEM")


def getDataFromXMLX509(url, u_key_file, u_cert_file, header = {'Python-urllib': ''}):
    "Extracts XML data from an URL feed using X509 certificates."
    class HTTPSClientAuthConnection(httplib.HTTPSConnection):
        def __init__(self, host, timeout=None):
            httplib.HTTPSConnection.__init__(self, host, key_file=u_key_file,cert_file=u_cert_file)
    class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
        def https_open(self, req):
            return self.do_open(HTTPSClientAuthConnection, req)

    output_data = None
    try:
        opener = urllib2.build_opener(urllib2.HTTPHandler(),HTTPSClientAuthHandler())
        req = urllib2.Request(url, None, header)
        output_data = opener.open(req).read()
    except Exception, e:
        output_data = None
    return output_data


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

        XML_Element_Feed = getDataFromXMLX509(settings.GOCDB_SERVICETYPE_URL,\
                                        settings.HOST_KEY, settings.HOST_CERT)
        Root = ElementTree.XML(XML_Element_Feed)
        Feed_List = []
        for element in Root.findall("SERVICE_TYPE"):
            Element_List = {}
            if element.getchildren():
                for child_element in element.getchildren():
                    Element_List[string.lower(child_element.tag)] = (child_element.text)
            Feed_List.append(Element_List)

        for fo in fos:
            fo.close()

    except IOError as e:
        logger.error(e)
        sys.exit(1)

    except Exception as e:
        logger.error("Error parsing service flavours")
        sys.exit(1)

    sfindb = set([sf.name for sf in models.ServiceFlavour.objects.all()])
    if len(sfindb) != len(Feed_List):
        sfs = set([(feed['service_type_name'], feed['service_type_desc']) \
                for feed in Feed_List])
        cur = connection.cursor()
        if len(sfindb) < len(Feed_List):
            cur.executemany('INSERT INTO poem_serviceflavour VALUES (?,?)', \
                    sfs.difference(sfindb))
            logger.info("Added %d service flavours" %\
                        (len(Feed_List) - len(sfindb)))
        elif len(sfindb) > len(Feed_List):
            cur.executemany('DELETE FROM poem_serviceflavour WHERE name IN (?,?)', \
                    sfindb.difference(sfs))
            logger.info("Deleted %d service flavours" %\
                        (len(sfindb) - len(Feed_List)))
        transaction.commit_unless_managed()
        connection.close()
    else:
        print "POEM - INFO - Service Flavours database is up to date"

main()
