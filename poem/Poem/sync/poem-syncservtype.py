import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Poem.settings')
django.setup()

import Poem.django_logging
import base64
import http.client
import logging
import os
import ssl

from Poem import settings
from Poem.poem import models
from Poem.tenants.models import Tenant
from django.db import connection, transaction
from xml.etree import ElementTree
from urllib.parse import urlparse
from configparser import ConfigParser

from tenant_schemas.utils import schema_context, get_public_schema_name

logging.basicConfig(format='%(filename)s[%(process)s]: %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger("POEM")


def tenant_servtype_data(tenant):
    config = ConfigParser()
    config.read(settings.CONFIG_FILE)

    HTTPAUTH = config.getboolean('SYNC_' + tenant.upper(), 'useplainhttpauth')
    HTTPUSER = config.get('SYNC_' + tenant.upper(), 'httpuser')
    HTTPPASS = config.get('SYNC_' + tenant.upper(), 'httppass')
    SERVICETYPE_URL = config.get('SYNC_' + tenant.upper(), 'servicetype')

    return {'HTTPAUTH': HTTPAUTH, 'HTTPUSER': HTTPUSER, 'HTTPPASS': HTTPPASS,
            'SERVICETYPE_URL': SERVICETYPE_URL}


def main():
    "Parses service flavours list from GOCDB"

    schemas = list(Tenant.objects.all().values_list('schema_name', flat=True))
    schemas.remove(get_public_schema_name())

    for schema in schemas:
        with schema_context(schema):
            tenant = Tenant.objects.get(schema_name=schema)
        data = tenant_servtype_data(tenant.name)

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

        o = urlparse(data['SERVICETYPE_URL'])
        try:
            if o.scheme.startswith('https'):
                context = ssl.create_default_context(cafile=settings.CAFILE,
                                                     capath=settings.CAPATH)
                conn = http.client.HTTPSConnection(host=o.netloc, \
                                               key_file=settings.HOST_KEY, cert_file=settings.HOST_CERT, \
                                               timeout=60,
                                               context=context)
            else:
                conn = http.client.HTTPConnection(host=o.netloc)

            headers = dict()
            if data['HTTPAUTH']:
                userpass_ascii = '{0}:{1}'.format(data['HTTPUSER'],
                                                  data['HTTPPASS'])
                userpass = base64.b64encode(userpass_ascii.encode())
                headers={'Authorization': 'Basic ' + userpass.decode()}

            conn.request('GET', o.path + '?' + o.query, headers=headers)
            ret = conn.getresponse().read()

        except Exception as e:
            logger.error("Error service flavours feed - %s" % (repr(e)))
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
                    Element_List[str(child_element.tag).lower()] = (child_element.text)
            Feed_List.append(Element_List)


        sfindb = set([(sf.name, sf.description) for sf in models.ServiceFlavour.objects.all()])
        if len(sfindb) != len(Feed_List):
            sfs = set([(feed['service_type_name'], feed['service_type_desc']) \
                    for feed in Feed_List])
            cur = connection.cursor()
            try:
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
                connection.close()
            except Exception as e:
                logger.error("database operations failed - %s" % e)
        else:
            logger.info("Service Flavours database is up to date")

main()
