from ajax_select import LookupChannel
from Poem.poem.models import VO, ServiceFlavour, MetricInstance
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
        values = check_cache(request, self.model, 'metric')
        return sorted(filter(lambda x: q.lower() in x.lower(), values))
