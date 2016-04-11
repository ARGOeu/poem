from ajax_select import LookupChannel
from Poem.poem.models import VO, ServiceFlavour, Metrics, MetricInstance, Tags, Probe
from django.core.cache import cache

def check_cache(request, model, attr):
    if not cache.get(request):
        values = set([eval('obj.' + attr) for obj in model.objects.all()])
        cache.set(request, values)
    else:
        values = cache.get(request)
    return values

class VOLookup(LookupChannel):
    model = VO

    def get_query(self, q, request):
        values = check_cache(request, self.model, 'name')
        return sorted(filter(lambda x: q.lower() in x.lower(), values))

class SFLookup(LookupChannel):
    model = ServiceFlavour

    def get_query(self, q, request):
        values = check_cache(request, self.model, 'name')
        return sorted(filter(lambda x: q.lower() in x.lower(), values))

class MILookup(LookupChannel):
    model = MetricInstance

    def get_query(self, q, request):
        values = check_cache(request, self.model, 'name')
        return sorted(filter(lambda x: q.lower() in x.lower(), values))

class MLookup(LookupChannel):
    model = Metrics
    relmodel = model.groupofmetrics_set.related.model

    def get_query(self, q, request):
        meting = []
        ugs = request.user.groupsofmetrics.values_list('name', flat=True)
        for u in ugs:
            meting += self.relmodel.objects.get(name=u).metrics.all().values_list('name', flat=True)
        return sorted(filter(lambda x: q.lower() in x.lower(), meting))

class PLookup(LookupChannel):
    model = Probe

    def get_query(self, q, request):
        values = check_cache(request, self.model, 'nameversion')
        return sorted(filter(lambda x: q.lower() in x.lower(), values))

class TLookup(LookupChannel):
    model = Tags

    def get_query(self, q, request):
        values = check_cache(request, self.model, 'name')
        return sorted(filter(lambda x: q.lower() in x.lower(), values))
