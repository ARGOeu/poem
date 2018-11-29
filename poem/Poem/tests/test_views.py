from django.test import TestCase

from Poem.poem.models import Profile, MetricInstance

import json

class ProfileViewsTests(TestCase):
    def setUp(self):
        self.profile = Profile.objects.create(
            name='ARGO_MON',
            version='1.0',
            vo='ops',
            description='Central ARGO-MON profile.',
            groupname='ARGO',
        )


    def test_get_profiles(self):

        MetricInstance.objects.create(
            profile=self.profile,
            service_flavour='APEL',
            metric='org.apel.APEL-Pub',
            vo='ops',
            fqan='fqan_text',
        )
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
                }
            ]
        )

    def test_get_profiles_with_no_fqan(self):

        MetricInstance.objects.create(
            profile=self.profile,
            service_flavour='APEL',
            metric='org.apel.APEL-Pub',
            vo='ops',
            fqan=None,
        )
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
                            'fqan': '',
                            'vo': 'ops',
                            'atp_service_type_flavour': 'APEL'
                        }
                    ]
                }
            ]
        )

    def test_get_profiles_with_no_profile_description(self):
        profile2 = Profile.objects.create(
            name='ARGO_MON_BIOMED',
            version='1.0',
            vo='biomed',
            description=None,
            groupname='ARGO',
        )

        MetricInstance.objects.create(
            profile=self.profile,
            service_flavour='APEL',
            metric='org.apel.APEL-Pub',
            vo='ops',
            fqan='fqan_text',
        )

        MetricInstance.objects.create(
            profile=profile2,
            service_flavour='APEL',
            metric='org.apel.APEL-Sync',
            fqan='something',
        )

        response = self.client.get('/api/0.2/json/profiles')
        data = json.loads(response.content)

        # sorting list of profiles because they are not always obtained in
        # the same order from api
        data = sorted(data, key=lambda k: k['name'])

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
                    'description': '',
                    'metric_instances': [
                        {
                            'metric': 'org.apel.APEL-Sync',
                            'fqan': 'something',
                            'vo': 'biomed',
                            'atp_service_type_flavour': 'APEL'
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

        profile4 = Profile.objects.create(
            name='TEST_PROFILE',
            description=None,
            vo='test',
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

        MetricInstance.objects.create(
            profile=profile4,
            service_flavour='TEST-FLAVOUR',
            metric='metric.for.testing',
            fqan=None,
        )

    def test_get_metrics_for_a_given_vo(self):
        with self.settings(POEM_NAMESPACE='hr.cro-ngi.TEST'):
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
                                'description': 'Central ARGO-MON_CRITICAL '
                                               'profile.',
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
        with self.settings(POEM_NAMESPACE='hr.cro-ngi.TEST'):
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
                                'description': 'Central ARGO-MON profile used '
                                               'for Biomed VO.',
                                'vo': 'biomed',
                                'metrics': [
                                    {
                                        'service_flavour': 'CREAM-CE',
                                        'name':
                                            'emi.cream.CREAMCE-'
                                            'AllowedSubmission',
                                        'fqan': ''
                                    }
                                ]
                            },
                            {
                                'name': 'ARGO_MON_CRITICAL',
                                'namespace': 'hr.cro-ngi.TEST',
                                'description': 'Central ARGO-MON_CRITICAL '
                                               'profile.',
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
        with self.settings(POEM_NAMESPACE='hr.cro-ngi.TEST'):
            response = self.client.get('/api/0.2/json/metrics_in_profiles/'
                                       '?vo_name=ops&profile=ARGO_MON')
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
        with self.settings(POEM_NAMESPACE='hr.cro-ngi.TEST'):
            response = self.client.get(
                '/api/0.2/json/metrics_in_profiles/?vo_name=ops&profile='
                'ARGO_MON&profile=ARGO_MON_CRITICAL')
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
                                'description': 'Central ARGO-MON_CRITICAL '
                                               'profile.',
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
        with self.settings(POEM_NAMESPACE='hr.cro-ngi.TEST'):
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
                                'description': 'Central ARGO-MON profile '
                                               'used for Biomed VO.',
                                'vo': 'biomed',
                                'metrics': [
                                    {
                                        'service_flavour': 'CREAM-CE',
                                        'name':
                                            'emi.cream.CREAMCE-Allowed'
                                            'Submission',
                                        'fqan': ''
                                    }
                                ]
                            }
                        ]
                    }
                ]
            )

    def test_get_metrics_without_vo(self):
        with self.settings(POEM_NAMESPACE='hr.cro-ngi.TEST'):
            response = self.client.get('/api/0.2/json/metrics_in_profiles/')

            self.assertEqual(response.content, b'Need the name of VO')

    def test_get_metric_with_no_valid_vo(self):
        with self.settings(POEM_NAMESPACE='hr.cro-ngi.TEST'):
            response = self.client.get(
                '/api/0.2/json/metrics_in_profiles/?vo_name=bla')

            self.assertEqual(response.content, b'Not valid VO')

    def test_get_metric_with_no_namespace(self):
        with self.settings(POEM_NAMESPACE=None):
            response=self.client.get(
                '/api/0.2/json/metrics_in_profiles/?vo_name=ops')

            data = json.loads(response.content)
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
                                'namespace': '',
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
                                'namespace': '',
                                'description': 'Central ARGO-MON_CRITICAL '
                                               'profile.',
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

    def test_get_metrics_with_no_profile_description(self):
        with self.settings(POEM_NAMESPACE='hr.cro-ngi.TEST'):
            response = self.client.get(
                '/api/0.2/json/metrics_in_profiles/?vo_name=test')

            data = json.loads(response.content)

            self.assertEqual(
                data,
                [
                    {
                        'name': ['test'],
                        'profiles': [
                            {
                                'name': 'TEST_PROFILE',
                                'namespace': 'hr.cro-ngi.TEST',
                                'description': '',
                                'vo': 'test',
                                'metrics': [
                                    {
                                        'service_flavour': 'TEST-FLAVOUR',
                                        'name': 'metric.for.testing',
                                        'fqan': ''
                                    }
                                ]
                            }
                        ]
                    }
                ]
            )
