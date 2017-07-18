from optparse import make_option
import sys
import Poem.django_logging
import logging
import json
import pprint
import codecs

from django.core.management.base import BaseCommand, CommandError

from Poem.poem.management.update_profile import PoemSync
from Poem.poem.models import Profile

logging.basicConfig(format='poem-exportprofiles[%(process)s]: %(levelname)s %(message)s')
logger = logging.getLogger('POEMIMPORTPROFILES')

class Command(BaseCommand):
    args = '[<space separated list of profiles to export>]'
    help = 'Export profiles from POEM to JSON formatted file'

    option_list = BaseCommand.option_list + (
                  make_option('--export',
                              action='store',
                              type='string',
                              help='Export profiles to a file',
                              dest='exportfile',
                              metavar='filename',
                              default=False),)

    def handle(self, *args, **options):
        if not options.get('exportfile'):
            raise CommandError('Usage is --export <file> %s' % self.args)

        lp = []
        for profile in Profile.objects.all():
            mifix = list()

            mi =  list(profile.metric_instances.all().\
                          values('metric', 'fqan', 'vo', 'service_flavour'))
            for m in mi:
                td = dict()
                for k, v in m.items():
                    if k == 'service_flavour':
                        td.update({'atp_service_type_flavour': v})
                    else:
                        td.update({k: v})
                mifix.append(td)
            lp.append({"name" : profile.name,
                       "vo" : profile.vo,
                       "version" : profile.version,
                       "description" : profile.description,
                       "metric_instances" : mifix
                     })

        profile_export = []
        for profile in lp:
            if args and profile['name'] not in args:
                continue
            profile_export.append(profile)

        with open(options.get('exportfile'), mode='w') as fp:
            json.dump(profile_export, fp, indent=4)

        if args:
            logger.info('Exported %s profiles to %s' % (' '.join(args), options.get('exportfile')))
        else:
            logger.info('Exported all profiles to %s' % (options.get('exportfile')))

