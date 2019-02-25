from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication

from rest_framework_api_key import models as api_models

from Poem.poem import models as poem_models

from .views import NotFound


class ListMetricsInGroup(APIView):
    authentication_classes = (SessionAuthentication,)

    def get(self, request, group):
        metrics = poem_models.Metrics.objects.\
            filter(groupofmetrics__name__exact=group).\
            values_list('name', flat=True)
        results = sorted(metrics, key=lambda m: m.lower())
        if results or (not results and
                       poem_models.GroupOfMetrics.objects.filter(
                           name__exact=group)):
            return Response({'result': results})
        else:
            raise NotFound(status=404,
                           detail='Group not found')


class ListTokens(APIView):
    authentication_classes = (SessionAuthentication,)

    def get(self, request):
        tokens = api_models.APIKey.objects.all().values_list('client_id', 'token')
        api_format = [dict(name=e[0], token=e[1]) for e in tokens]
        return Response(api_format)


class ListTokenForTenant(APIView):
    authentication_classes = (SessionAuthentication,)

    def get(self, request, name):
        try:
            e = api_models.APIKey.objects.get(client_id=name)

            return Response(e.token)

        except api_models.APIKey.DoesNotExist:
            raise NotFound(status=404,
                           detail='Tenant not found')


class ListUsers(APIView):
    authentication_classes = (SessionAuthentication,)

    def get(self, request):
        users = poem_models.CustUser.objects.all().values_list('username',
                                                               flat=True)
        results = sorted(users)
        return Response({'result': results})


class ListProbes(APIView):
    authentication_classes = (SessionAuthentication,)

    def get(self, request, probe_name):
        probes = poem_models.Probe.objects.get(name=probe_name)
        result = dict(id=probes.id,
                      name=probes.name,
                      description=probes.description,
                      comment=probes.comment)
        return Response(result)
