from rest_framework.test import APITestCase

from Poem.poem.models import *
from Poem.api.views_internal import *


class ListMetricsInGroupAPIViewTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ListMetricsInGroup.as_view()
        self.url = '/api/v2/internal/metrics/EOSC'

    def test_permission_denied_in_case_no_authorization(self):
        request = self.factory.get(self.url)
        response = self.view(request)
        self.assertEqual(response.status_code, 403)

    def test_status_code_in_case_nonexisting_site(self):
        url = '/api/v2/internal/metric/fake_group'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
