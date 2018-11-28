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

class MetricsInProfilesVIewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        profile1 = Profile.objects.create(
            name='ARGO_MON_CRITICAL',
            description='Central ARGO-MON_CRITICAL profile.',
            vo='ops',
            groupname='ARGO',
        )

        profile2 = Profile.objects.create(
            name='ARGO_MON_BIOMED',
            description='Central ARGO-MON profile used for Biomed VO.',
            vo='biomed',
            groupname='ARGO',
        )

        profile3 = Profile.objects.create(
            name='ARGO_MON',
            description='Central ARGO-MON profile.',
            vo='ops',
            groupname='ARGO',
        )

        MetricInstance.objects.create(
            profile=profile1,
            service_flavour='ARC-CE',
            metric='org.nordugrid.ARC-CE-ARIS',
            fqan=None,
        )

        MetricInstance.objects.create(
            profile=profile1,
            service_flavour='APEL',
            metric='org.apel.APEL-Pub',
            fqan=None,
        )

        MetricInstance.objects.create(
            profile=profile2,
            service_flavour='CREAM-CE',
            metric='emi.cream.CREAMCE-AllowedSubmission',
            fqan=None,
        )

        MetricInstance.objects.create(
            profile=profile3,
            service_flavour='APEL',
            metric='org.apel.APEL-Pub',
            fqan=None,
        )

    def test_get_metrics_for_a_given_vo(self):
        response = self.client.get(
            '/api/0.2/json/metrics_in_profiles/?vo_name=ops')
        data = json.loads(response.content)

        # sorting list of profiles because they are not always obtained in
        # the same order from api
        data[0]['profiles'] = sorted(data[0]['profiles'], key=lambda k: k[
            'name'])
        self.assertEqual(
            data,
            [
                {
                    'name': ['ops'],
                    'profiles': [
                        {
                            'name': 'ARGO_MON',
                            'namespace': 'hr.cro-ngi.TEST',
                            'description': 'Central ARGO-MON profile.',
                            'vo': 'ops',
                            'metrics': [
                                {
                                    'service_flavour': 'APEL',
                                    'name': 'org.apel.APEL-Pub',
                                    'fqan': ''
                                }
                            ]
                        },
                        {
                            'name': 'ARGO_MON_CRITICAL',
                            'namespace': 'hr.cro-ngi.TEST',
                            'description': 'Central ARGO-MON_CRITICAL profile.',
                            'vo': 'ops',
                            'metrics': [
                                {
                                    'service_flavour': 'APEL',
                                    'name': 'org.apel.APEL-Pub',
                                    'fqan': ''
                                },
                                {
                                    'service_flavour': 'ARC-CE',
                                    'name': 'org.nordugrid.ARC-CE-ARIS',
                                    'fqan': ''
                                }
                            ]
                        }
                    ]
                }
            ]
        )

    def test_get_metrics_for_multiple_vos(self):
        response = self.client.get(
            '/api/0.2/json/metrics_in_profiles/?vo_name=ops&vo_name=biomed')
        data = json.loads(response.content)

        # sorting list of profiles because they are not always obtained in
        # the same order from api
        data[0]['profiles'] = sorted(data[0]['profiles'], key=lambda k: k[
            'name'])

        self.assertEqual(
            data,
            [
                {
                    'name': ['ops', 'biomed'],
                    'profiles': [
                        {
                            'name': 'ARGO_MON',
                            'namespace': 'hr.cro-ngi.TEST',
                            'description': 'Central ARGO-MON profile.',
                            'vo': 'ops',
                            'metrics': [
                                {
                                    'service_flavour': 'APEL',
                                    'name': 'org.apel.APEL-Pub',
                                    'fqan': ''
                                }
                            ]
                        },
                        {
                            'name': 'ARGO_MON_BIOMED',
                            'namespace': 'hr.cro-ngi.TEST',
                            'description': 'Central ARGO-MON profile used for '
                                           'Biomed VO.',
                            'vo': 'biomed',
                            'metrics': [
                                {
                                    'service_flavour': 'CREAM-CE',
                                    'name':
                                        'emi.cream.CREAMCE-AllowedSubmission',
                                    'fqan': ''
                                }
                            ]
                        },
                        {
                            'name': 'ARGO_MON_CRITICAL',
                            'namespace': 'hr.cro-ngi.TEST',
                            'description': 'Central ARGO-MON_CRITICAL profile.',
                            'vo': 'ops',
                            'metrics': [
                                {
                                    'service_flavour': 'APEL',
                                    'name': 'org.apel.APEL-Pub',
                                    'fqan': ''
                                },
                                {
                                    'service_flavour': 'ARC-CE',
                                    'name': 'org.nordugrid.ARC-CE-ARIS',
                                    'fqan': ''
                                }
                            ]
                        }
                    ]
                }
            ]
        )

    def test_get_metrics_for_a_given_vo_and_a_given_profile(self):
        response = self.client.get(
            '/api/0.2/json/metrics_in_profiles/?vo_name=ops&profile=ARGO_MON')
        data = json.loads(response.content)

        self.assertEqual(
            data,
            [
                {
                    'name': ['ops'],
                    'profiles': [
                        {
                            'name': 'ARGO_MON',
                            'namespace': 'hr.cro-ngi.TEST',
                            'description': 'Central ARGO-MON profile.',
                            'vo': 'ops',
                            'metrics': [
                                {
                                    'service_flavour': 'APEL',
                                    'name': 'org.apel.APEL-Pub',
                                    'fqan': ''
                                }
                            ]
                        }
                    ]
                }
            ]
        )

    def test_get_metrics_for_a_given_vo_and_multiple_profiles(self):
        response = self.client.get(
            '/api/0.2/json/metrics_in_profiles/?vo_name=ops&profile=ARGO_MON'
            '&profile=ARGO_MON_CRITICAL')
        data = json.loads(response.content)

        data[0]['profiles'] = sorted(data[0]['profiles'], key=lambda k: k[
            'name'])

        self.assertEqual(
            data,
            [
                {
                    'name': ['ops'],
                    'profiles':[
                        {
                            'name': 'ARGO_MON',
                            'namespace': 'hr.cro-ngi.TEST',
                            'description': 'Central ARGO-MON profile.',
                            'vo': 'ops',
                            'metrics': [
                                {
                                    'service_flavour': 'APEL',
                                    'name': 'org.apel.APEL-Pub',
                                    'fqan': ''
                                }
                            ]
                        },
                        {
                            'name': 'ARGO_MON_CRITICAL',
                            'namespace': 'hr.cro-ngi.TEST',
                            'description': 'Central ARGO-MON_CRITICAL profile.',
                            'vo': 'ops',
                            'metrics': [
                                {
                                    'service_flavour': 'APEL',
                                    'name': 'org.apel.APEL-Pub',
                                    'fqan': ''
                                },
                                {
                                    'service_flavour': 'ARC-CE',
                                    'name': 'org.nordugrid.ARC-CE-ARIS',
                                    'fqan': ''
                                }
                            ]
                        }
                    ]
                }
            ]
        )

    def test_get_metrics_for_multiple_vos_and_multiple_profiles(self):
        response = self.client.get(
            '/api/0.2/json/metrics_in_profiles/?vo_name=ops&vo_name=biomed'
            '&profile=ARGO_MON&profile=ARGO_MON_BIOMED')
        data = json.loads(response.content)

        data[0]['profiles'] = sorted(data[0]['profiles'], key=lambda k: k[
            'name'])

        self.assertEqual(
            data,
            [
                {
                    'name': ['ops', 'biomed'],
                    'profiles': [
                        {
                            'name': 'ARGO_MON',
                            'namespace': 'hr.cro-ngi.TEST',
                            'description': 'Central ARGO-MON profile.',
                            'vo': 'ops',
                            'metrics': [
                                {
                                    'service_flavour': 'APEL',
                                    'name': 'org.apel.APEL-Pub',
                                    'fqan': ''
                                }
                            ]
                        },
                        {
                            'name': 'ARGO_MON_BIOMED',
                            'namespace': 'hr.cro-ngi.TEST',
                            'description': 'Central ARGO-MON profile used for '
                                           'Biomed VO.',
                            'vo': 'biomed',
                            'metrics': [
                                {
                                    'service_flavour': 'CREAM-CE',
                                    'name':
                                        'emi.cream.CREAMCE-AllowedSubmission',
                                    'fqan': ''
                                }
                            ]
                        }
                    ]
                }
            ]
        )
