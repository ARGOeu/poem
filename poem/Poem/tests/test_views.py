from django.test import TestCase

from Poem.poem.models import Profile, MetricInstance

import json

class ProfileViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        profile1 = Profile.objects.create(
            name='ARGO_MON',
            version='1.0',
            vo='ops',
            description='Central ARGO-MON profile.',
            groupname='ARGO',
        )

        profile2 = Profile.objects.create(
            name='ARGO_MON_BIOMED',
            version='1.0',
            vo='biomed',
            description='Central ARGO-MON profile used for Biomed VO.',
            groupname='ARGO',
        )

        MetricInstance.objects.create(
            profile=profile1,
            service_flavour='APEL',
            metric='org.apel.APEL-Pub',
            vo='ops',
            fqan='fqan_text',
        )

        MetricInstance.objects.create(
            profile=profile2,
            service_flavour='ARC-CE',
            metric='org.nordugrid.ARC-CE-ARIS',
            vo='biomed',
            fqan=None,
        )

    def test_get_profiles(self):
        response = self.client.get('/api/0.2/json/profiles')
        data = json.loads(response.content)
        self.assertEqual(
            data,
            [
                {
                    'name': 'ARGO_MON',
                    'atp_vo': 'ops',
                    'version': '1.0',
                    'description': 'Central ARGO-MON profile.',
                    'metric_instances': [
                        {
                            'metric': 'org.apel.APEL-Pub',
                            'fqan': 'fqan_text',
                            'vo': 'ops',
                            'atp_service_type_flavour': 'APEL'
                        }
                    ]
                },
                {
                    'name': 'ARGO_MON_BIOMED',
                    'atp_vo': 'biomed',
                    'version': '1.0',
                    'description': 'Central ARGO-MON profile used for Biomed '
                                   'VO.',
                    'metric_instances': [
                        {
                            'metric': 'org.nordugrid.ARC-CE-ARIS',
                            'fqan': '',
                            'vo': 'biomed',
                            'atp_service_type_flavour': 'ARC-CE',
                        }
                    ]
                }
            ]
        )
