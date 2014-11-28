#!/usr/bin/python

import string
import sys
import urllib2
import httplib
import logging
import Poem.django_logging
from Poem import settings
from Poem.poem import models
from django.db import connection, transaction
from xml.etree import ElementTree

logger = logging.getLogger("POEM")


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
    Root = ElementTree.XML(vo_xml)
    idcards = Root.findall("IDCard")
    if len(idcards) > 0:
        vos = []
        for vo_element in idcards:
            dict_vo_element = dict(vo_element.items())
            if dict_vo_element.has_key('Name') == False or dict_vo_element.has_key('Status') == False:
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
        transaction.commit_unless_managed()
        connection.close()
    else:
        print "POEM - INFO - VO database is up to date"

main()
