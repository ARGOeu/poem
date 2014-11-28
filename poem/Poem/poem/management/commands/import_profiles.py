from optparse import make_option
import sys
import Poem.django_logging
import logging

from django.core.management.base import BaseCommand, CommandError

from Poem.poem.management.update_profile import PoemSync
from Poem.poem.models import Profile

logger = logging.getLogger('POEM')
class Command(BaseCommand):
    args = '<space separated list of profiles to import>'
    help = 'Import profiles to POEM (from URL containing JSON encoded List)'

    option_list = BaseCommand.option_list + (
                 make_option('--url',
                             action='store',
                             help='URL containing JSON encoded list of profiles',
                             dest='url',
                             default=None),
                 make_option('--initial',
                             action='store_true',
                             help='Only import profiles if poem database is empty',
                             dest='is_initial',
                             default=False),
                 )

    def handle(self, *args, **options):
        logger.info( "Running synchronizer for POEM sync")
        #sync_ob.sync_expression_list_from_url('file:///root//workspace/poem/poem_sync/Poem_sync/poem_sync/fixtures/api/0.1/expressions')
        #sync_ob.sync_profile_list_from_url('file:///root//workspace/poem/poem_sync/Poem_sync/poem_sync/fixtures/api/0.1/profiles')
        if not options.get('url'):
            raise CommandError('Usage is %s' % self.args)
        if args and options.get('is_mddb'):
            raise CommandError('Usage is %s' % self.args)
        if options.get('is_initial') and Profile.objects.all():
            logger.warning('Database already contains profiles .. skipping.')
            sys.exit(0)

        try:
            if args:
                sync_ob = PoemSync(profile_list=args)
                sync_ob.sync_profile_list_from_url(url=options.get('url'))
        except Exception, e:
            logger.error('Exception occured while trying to import profiles (%s)' % str(e))
            sys.exit(2)
