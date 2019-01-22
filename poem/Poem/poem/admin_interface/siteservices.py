from django.contrib import admin

from Poem.poem.models import Service, MetricInstance, Metric


class ServiceAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('/poem_media/css/siteservices.css',)}

    qs = Service.objects.all()
    service_area = [p.service_area for p in qs]
    service_name = [p.service_name for p in qs]
    service_type = [p.service_type for p in qs]
    data = list()
    for i in range(len(service_type)):
        mi = MetricInstance.objects.filter(service_flavour=service_type[i])
        metric = list(set(mi))
        for j in range(len(metric)):
            try:
                probe = Metric.objects.get(name=metric[j].metric)
                probe = probe.probeversion
            except Metric.DoesNotExist:
                pass
            else:
                if probe == '':
                    pass
                else:
                    data.append({'service_area': service_area[i],
                                 'service_name': service_name[i],
                                 'service_type': service_type[i],
                                 'metric': metric[j].metric,
                                 'probe': probe})

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['servicedata'] = self.data
        return super(ServiceAdmin, self).changelist_view(request, extra_context=extra_context)
