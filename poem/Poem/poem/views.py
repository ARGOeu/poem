from django.shortcuts import render_to_response
from django.conf import settings

from Poem.poem import models

def profiles(request):
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
    lp = []
    for profile in models.Profile.objects.all():
        lp.append({"name" : profile.name, "vo" : profile.vo,
                   "version" : profile.version, "owner" : profile.owner,
                   "description" : profile.description,
                   "metric_instances" : profile.metric_instances.all().\
                                  values('metric', 'fqan', 'vo', 'service_flavour')
                   })

    return render_to_response('profiles', {'result' : lp}, mimetype='application/json')

def metrics_in_profiles(request):
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
                                        'metrics' : [m for m in metrics \
                                                    if m['profile__name'] == p[0]]})
        result = {"name" : lookup, "profiles" : metrics_in_profiles}
        return render_to_response('metrics_in_profiles', \
                                  {'result' : result}, \
                                  mimetype='application/json')
    else:
        return "Need the name of VO"
