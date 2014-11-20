from optparse import make_option
import sys
import Poem.django_logging
import logging

from django.core.management.base import BaseCommand, CommandError
try:
    import Poem.settings
except ImportError:
    sys.stderr.write("Couldn't find the settings.py module.")
    sys.exit(1)

from Poem.poem.models import Profile

logger = logging.getLogger('POEM')
class Command(BaseCommand):
    help = 'Tag set of profiles'
    args = '<space separated list of profiles to tag>'

    option_list = BaseCommand.option_list + (
                 make_option('--tag',
                             action='store',
                             help='A string representing the tag',
                             dest='tag',
                             default=None),
                 )

    def handle(self, *args, **options):
        if not options.get('tag'):
            raise CommandError('Usage is %s' % self.args)
        
        if not args:
            raise CommandError('Usage is %s' % self.args)
        
        for profile_name in args:
            try:
                profile = Profile.objects.get(name=profile_name)
                profile.tags.add(options.get('tag'))
            except Exception, e:
                logger.error('Exception occurred while trying to tag profile %s (%s)' % (str(e), 
                                                                                       profile_name))
                sys.exit(2)
            
        logger.info( "All profiles were tagged successfully.")    
        
        
