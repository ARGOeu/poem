from rest_framework.test import APITestCase, APIRequestFactory, \
    force_authenticate
from rest_framework import status

from Poem.poem.models import *
from Poem.api.views_internal import *


class ListMetricsInGroupAPIViewTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ListMetricsInGroup.as_view()
        self.url = '/api/v2/internal/metrics/EOSC'
        self.user = CustUser.objects.create(username='testuser')

        metric1 = Metrics.objects.create(name='org.apel.APEL-Pub')
        metric2 = Metrics.objects.create(name='org.apel.APEL-Sync')

        group1 = GroupOfMetrics.objects.create(name='EOSC')
        group1.metrics.create(name=metric1.name)
        group1.metrics.create(name=metric2.name)

        GroupOfMetrics.objects.create(name='Empty_group')

    def test_permission_denied_in_case_no_authorization(self):
        request = self.factory.get(self.url)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_status_code_in_case_nonexisting_site(self):
        url = '/api/v2/internal/metrics/fake_group'
        request = self.factory.get(url)
        force_authenticate(request, user=self.user)
        response = self.view(request, 'fake_group')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_metrics_in_group_for_a_given_group(self):
        request = self.factory.get(self.url)
        force_authenticate(request, user=self.user)
        response = self.view(request, 'EOSC')
        self.assertEqual(
            response.data,
            {
                'result': ['org.apel.APEL-Pub', 'org.apel.APEL-Sync']
            }
        )
