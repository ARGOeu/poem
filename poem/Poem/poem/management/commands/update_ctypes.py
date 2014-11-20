import Poem.django_logging
import logging

from django.core.management.base import BaseCommand
from django.core.management import setup_environ

logger = logging.getLogger('POEM')
try:
    import Poem.settings
except ImportError:
    import sys
    logger.error("Couldn't find the settings.py module.")
    sys.exit(1)

class Command(BaseCommand):
    help = 'Update Django content types.'

    def handle(self, *args, **options):
        setup_environ(Poem.settings)
        # Add any missing content types
        from django.contrib.contenttypes.management \
            import update_all_contenttypes
        update_all_contenttypes()

        logger.info('Content types were successfully updated.')