from django.shortcuts import render_to_response
from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View
from Poem.poem import models
import json

class Profiles(View):
    """
    Dumps the list of profiles available in this namespace. This API call is used by the
    poem-sync synchronizer to get list of profiles and their attributes. Sample output:
    ::
        [ {
        "name": "ALICE",
        "atp_vo": "alice",
        "metric_instances": [
            {
                "atp_service_type_flavour": "CE",
                "fqan": "",
                "metric": "org.sam.CE-JobSubmit",
                "vo": "alice"
            }, ....
        ] ]

    * *Supported formats*: json
    * *URL*: /api/0.2/json/profiles
    * *Supported methods*: GET
    """
    def get(self, request):
        lp = []
        for profile in models.Profile.objects.all():
            mi = list(profile.metric_instances.all().\
                 values('metric', 'fqan', 'vo', 'service_flavour'))
            mi = map(lambda e: {'metric': e['metric'],\
                                'fqan': e['fqan'],\
                                'vo': e['vo'],\
                                'atp_service_type_flavour': e['service_flavour']}, mi)
            lp.append({"name": profile.name, "atp_vo" : profile.vo,
                    "version": profile.version,
                    "description": profile.description,
                    "metric_instances": mi})

        return HttpResponse(json.dumps(lp), mimetype='application/json')

class MetricsInProfiles(View):
    """
    Dumps all metrics, service flavours and profile names
    for a given VO. Example:

    {
        "name": "ops",
        "profiles": [
            {
                "metrics": [
                    {
                        "service_flavour": "APEL",
                        "fqan": "",
                        "name": "org.apel.APEL-Pub",
                        "profile__name": "ROC_OPERATORS"
                    },
                    {
                        "service_flavour": "ARC-CE",
                        "fqan": "",
                        "name": "org.nordugrid.ARC-CE-ARIS",
                        "profile__name": "ROC_OPERATORS"
                    },
                ],
                "namespace": "CH.CERN.SAM",
                "name": "ROC_OPERATORS",
                "description": "The main profile that contains Operations tests."
            },
        ]
    }

    * *Supported formats*: json
    * *URL*: /api/0.2/json/metrics_in_profiles/?vo_name=ops
    * *Supported methods*: GET
    """

    def get(self, request):
        lookup = request.GET.get('vo_name')
        if lookup:
            metrics = {}
            metrics = models.MetricInstance.objects.filter(vo__exact=lookup).values('metric', 'service_flavour', 'fqan', 'profile__name')
            profiles = set(models.MetricInstance.objects.filter(vo__exact=lookup).values_list('profile__name', 'profile__description'))
            metrics_in_profiles = []
            for p in profiles:
                metrics_in_profiles.append({'name' : p[0], \
                                            'namespace' : settings.POEM_NAMESPACE, \
                                            'description' : p[1], \
                                            'metrics' : [{'service_flavour': m['service_flavour'], \
                                                          'name': m['metric'], \
                                                          'fqan': m['fqan']} for m in metrics \
                                                        if m['profile__name'] == p[0]]})
            result = {"name" : lookup, "profiles" : metrics_in_profiles}

            return HttpResponse(json.dumps([result]), mimetype='application/json')

        else:
            return HttpResponse("Need the name of VO")

class MetricsInGroup(View):
    def get(self, request):
        gr = request.GET.get('group')
        metrics = models.Metrics.objects.filter(groupofmetrics__name__exact=gr).values_list('name', flat=True)
        return HttpResponse(json.dumps({'result': [met for met in metrics]}), content_type='application/json')

class Metrics(View):
    def get(self, request):
        api = list()
        tag = request.GET.get('tag')
        if tag:
            try:
                tagobj = models.Tags.objects.get(name__iexact=tag)
                metricsobjs = models.Metric.objects.filter(tag=tagobj)
                for m in metricsobjs:
                    mdict = dict()
                    mdict.update({m.name: dict()})

                    exe = models.MetricProbeExecutable.objects.get(metric=m)
                    mdict[m.name].update({'probe': exe.value})

                    mc = models.MetricConfig.objects.filter(metric=m)
                    mdict[m.name].update({'config': dict()})
                    for config in mc:
                        mdict[m.name]['config'].update({config.key: config.value})

                    f = models.MetricFlags.objects.filter(metric=m)
                    mdict[m.name].update({'flags': dict()})
                    for flag in f:
                        mdict[m.name]['flags'].update({flag.key: flag.value})

                    md = models.MetricDependancy.objects.filter(metric=m)
                    mdict[m.name].update({'dependency': dict()})
                    for dependancy in md:
                        mdict[m.name]['dependency'].update({dependancy.key: dependancy.value})

                    ma = models.MetricAttribute.objects.filter(metric=m)
                    mdict[m.name].update({'attribute': dict()})
                    for attribute in ma:
                        mdict[m.name]['attribute'].update({attribute.key: attribute.value})

                    mp = models.MetricParameter.objects.filter(metric=m)
                    mdict[m.name].update({'parameter': dict()})
                    for parameter in mp:
                        mdict[m.name]['parameter'].update({parameter.key: parameter.value})

                    version_fields = json.loads(m.probekey.serialized_data)

                    mdict[m.name].update({'docurl': version_fields[0]['fields']['docurl']})
                    api.append(mdict)
            except models.Tags.DoesNotExist:
                pass

        return HttpResponse(json.dumps(api), content_type='application/json')
