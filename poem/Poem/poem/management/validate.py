import Poem.django_logging
import logging

from Poem.poem.models import Profile

class ProfileValidation(object):
    
    def __init__(self):
        self.log = logging.getLogger('POEM')
        #self.log.info('Profile validation initialized.')
        
    def run(self):
        # if profiles are referencing deleted ATP groups mark
        # them as invalid
        profiles = Profile.objects.filter(groups__is_deleted='Y')
        if profiles:
            self.log.info('Profiles %s marked as invalid' % (str(profiles)) )
            profiles.update(valid=False)
        
        self.log.info('Profile validation completed successfully.')
        