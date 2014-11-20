import Poem.django_logging
import logging

from django.core.management.base import BaseCommand
from django.core.management import setup_environ
try:
    import Poem.settings
except ImportError:
    import sys
    sys.stderr.write("Couldn't find the settings.py module.")
    sys.exit(1)

logger = logging.getLogger('POEM')
class Command(BaseCommand):
    help = 'Update Django permissions'

    def handle(self, *args, **options):
        setup_environ(Poem.settings)
        from django.contrib.auth.management import create_permissions
        from django.db.models import get_apps
        
        for app in get_apps():
            create_permissions(app, None, 2)
        logger.info('Permissions were successfully updated.')