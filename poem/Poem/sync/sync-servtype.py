#!/usr/bin/python

import string
import sys
import urllib2
import httplib
import os
from Poem import settings
from Poem.poem import models
from django.db import connection, transaction

if sys.version_info[:2] >= (2, 6):
    from xml.etree import ElementTree as ET
else:
    from elementtree import ElementTree as ET

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


    try:
        XML_Element_Feed = getDataFromXMLX509(settings.GOCDB_SERVICETYPE_URL,\
                                        settings.HOST_KEY, settings.HOST_CERT)
        Root = ET.XML(XML_Element_Feed)
        Feed_List = []
        for element in Root.findall("SERVICE_TYPE"):
            Element_List = {}
            if element.getchildren():
                for child_element in element.getchildren():
                    Element_List[string.lower(child_element.tag)] = (child_element.text)
            Feed_List.append(Element_List)
    except Exception, e:
        settings.config.logger.error("GOCDB Topology - Execution - Error parsing service flavours")
        settings.config.logger_syslog.error("GOCDB Topology - Execution - Error parsing service flavours")
        sys.exit(1)

    sfindb = set([sf.name for sf in models.ServiceFlavour.objects.all()])
    if len(sfindb) != len(Feed_List):
        sfs = set([(feed['service_type_name'], feed['service_type_desc']) \
                for feed in Feed_List])
        cur = connection.cursor()
        if len(sfindb) < len(Feed_List):
            cur.executemany('INSERT INTO poem_serviceflavour VALUES (?,?)', \
                    sfs.difference(sfindb))
        elif len(sfindb) > len(Feed_List):
            cur.executemany('DELETE FROM poem_serviceflavour WHERE name IN (?,?)', \
                    sfindb.difference(sfs))
        transaction.commit_unless_managed()
        connection.close()

main()
