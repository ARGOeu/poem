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
                    context = ssl.create_default_context(
                        cafile=settings.CAFILE,
                        capath=settings.CAPATH
                    )
                    conn = http.client.HTTPSConnection(
                        host=o.netloc,
                        key_file=settings.HOST_KEY,
                        cert_file=settings.HOST_CERT,
                        timeout=60,
                        context=context
                    )
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
                logger.error("%s: Error service flavours feed - %s" % (
                    schema.upper(), repr(e)))
                raise SystemExit(1)

            try:
                Root = ElementTree.XML(ret)
            except Exception as e:
                logger.error("%s: Error parsing service flavours - %s" % (
                    schema.upper(), e))
                raise SystemExit(1)

            elements = Root.findall("SERVICE_TYPE")
            if not elements:
                logger.error("%s: Error parsing service flavours"
                             % schema.upper())
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
                try:
                    if len(sfindb) < len(Feed_List):
                        for flavour in sfs.difference(sfindb):
                            models.ServiceFlavour.objects.create(
                                name=flavour[0],
                                description=flavour[1]
                            )
                        logger.info("%s: Added %d service flavours"
                                    % (schema.upper(),
                                       (len(Feed_List) - len(sfindb))))
                    elif len(sfindb) > len(Feed_List):
                        for flavour in sfindb.difference(sfs):
                            models.ServiceFlavour.objects.filter(
                                name=flavour[0],
                                description=flavour[1]
                            ).delete()
                        logger.info("%s: Deleted %d service flavours"
                                    % (schema.upper(),
                                       (len(sfindb) - len(Feed_List))))
                except Exception as e:
                    logger.error("%s: database operations failed - %s"
                                 % (schema.upper(), e))
            else:
                logger.info("%s: Service Flavours database is up to date"
                            % schema.upper())

main()
