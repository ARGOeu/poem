#!/usr/bin/python

import string
import sys
import urllib2
import httplib
from Poem import settings
from Poem.poem import models
from django.db import connection, transaction

if sys.version_info[:2] >= (2, 6):
    from xml.etree import ElementTree as ET
else:
    from elementtree import ElementTree as ET

def getDataFromXML(url):
    "Extracts XML data from an URL feed."
    output_data = None
    try:
        output_data = urllib2.urlopen(url).read()
    except Exception, e:
        output_data = None
    return output_data

def main():
    "Parses VO list provided by CIC portal"

    vo_xml = getDataFromXML(settings.CIC_VO_URL)
		# "http://operations-portal.egi.eu/xml/voIDCard/public/all/true")
    Root = ET.XML(vo_xml)
    idcards = Root.findall("IDCard")
    if len(idcards) > 0:
        vos = []
        for vo_element in idcards:
            dict_vo_element = dict(vo_element.items())
            if dict_vo_element.has_key('Name') == False or dict_vo_element.has_key('Status') == False:
                print "CIC - Validation - vo card does not contain 'Name' and 'Status' attributes for %s" % vo_element
            else:
                if dict_vo_element['Status'].lower() == 'production' and dict_vo_element['Name'] != '':
                    vos.append(dict_vo_element['Name'])
    else:
        print "CIC - Validation - Exiting synchronizer due to invalid VO card"
        settings.config.logger.error("CIC - Validation - Exiting synchronizer due to invalid VO card")
        settings.config.logger_syslog.error("CIC - Validation - Exiting synchronizer due to invalid VO card")

    voindb = set([(vo.name,) for vo in models.VO.objects.all()])
    if len(voindb) != len(vos):
        svos = set([(vo,) for vo in vos])
        cur = connection.cursor()
        if len(voindb) < len(vos):
            cur.executemany('INSERT INTO poem_vo VALUES (?)', svos.difference(voindb))
        elif len(voindb) > len(vos):
            cur.executemany('DELETE FROM poem_vo WHERE name IN (?)', voindb.difference(svos))
        transaction.commit_unless_managed()
        connection.close()

main()
