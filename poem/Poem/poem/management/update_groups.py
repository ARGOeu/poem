import Poem.django_logging
import logging
import sys
from urllib import urlopen

from django.utils import simplejson
from django.conf import settings

from Poem.poem.models import GroupReference

class GroupSync(object):
    """ Synchronize ATP groups """

    def __init__(self):
        self.atp_url = '%s' % (settings.ATP_URL+'/atp/api/groups/json')
        self.log = logging.getLogger('POEM')
        #self.log.info('ATP GroupSync initialized.')
        
    def run(self):
        try:
            atp_groups = simplejson.JSONDecoder().decode(urlopen(self.atp_url).read())
        except IOError, e:
            self.log.error("Failed to retrieve the feed: %s" % (self.atp_url))
            sys.exit(2)
        except Exception, e:
            self.log.error("Exception occurred while retrieving the feed (%s, %s)" % (self.atp_url, str(e)) )
            sys.exit(2)
        
        try:
            atp_groups = set([ (g['group_type']['typename'], 
                                g['groupname'], 
                                g['isdeleted'], 
                                g['description']) for g in atp_groups ])
        except Exception, e:
            self.log.error("Exception occurred while parsing the ATP groups (API error?) (%s)" % (e))
            sys.exit(2)
            
        local_groups = set(GroupReference.objects.distinct().all().values_list(
                                                        'atp_grouptype', 'atp_groupname', 
                                                        'is_deleted', 'description'))
        
        self.add_update(atp_groups, local_groups)
        # fetch local_groups again to include updated objects
        local_groups = set(GroupReference.objects.distinct().all().values_list(
                                                        'atp_grouptype', 'atp_groupname', 
                                                        'is_deleted', 'description'))
        self.remove(atp_groups, local_groups)
        
        self.log.info('ATP GroupSync terminated successfully.')
    
    def add_update(self, set1, set2):
        to_add = set1 - set2
        for g in to_add:
            try:
                gr, created = GroupReference.objects.get_or_create(atp_grouptype=g[0],
                               atp_groupname=g[1])
                # handle updates properly
                gr.is_deleted = g[2]
                gr.description = g[3]
                if created:
                    self.log.debug('Adding %s ' % (str(g)) )
                else:
                    self.log.debug('Updating %s' % (str(g)) )
                gr.save()
            except Exception, e:
                self.log.error('Exception caught while adding (%s,%s)' % (str(g), str(e)) )
                sys.exit(2)
                
    
    def remove(self, set1, set2):
        to_remove = set2 - set1
        for g in to_remove:
            g_qs = GroupReference.objects.filter(atp_grouptype=g[0], 
                                              atp_groupname=g[1],
                                              is_deleted=g[2],
                                              description=g[3])
            self.log.debug('Removing %s' % (str(g)) )
            
            if len(g_qs) != 1:
                self.log.warning("Single object assertion failed while removing (%s)." % (str(g)))
                continue
            
            try:
                g_qs.delete()
            except Exception, e:
                self.log.error("Exception caught while removing (%s, %s). " % (str(g), str(e)) )
                sys.exit(2)

    
    