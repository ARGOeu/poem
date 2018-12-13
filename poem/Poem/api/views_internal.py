from rest_framework.views import APIView
from rest_framework.response import Response

from Poem.poem import models


class ListMetricsInGroup(APIView):
    def get(self, request, group):
        metrics = models.Metrics.objects.\
            filter(groupofmetrics__name__exact=group).\
            values_list('name', flat=True)
        results = sorted(metrics, key=lambda m: m.lower())
        return Response({'result': results})
