from django.conf.urls.defaults import patterns, url
from piston import resource

from Poem.poem_api import handlers

urlpatterns = patterns('',
    # Backward compatible API
    url(r'^0.1/(?P<emitter_format>.+)/namespace/$',
                            resource.Resource(handler=handlers.NamespaceHandler)),
    url(r'^0.1/(?P<emitter_format>.+)/metricinstances/$',
                            resource.Resource(handler=handlers.MetricInstanceHandler)),
    url(r'^0.1/json/hints/metrics/$',
                            resource.Resource(handler=handlers.MetricHandler),
                            name='poem_metric_hints'),
    url(r'^0.1/json/profiles/$',
                            resource.Resource(handler=handlers.CompProfileHandler)),
    url(r'^0.1/json/profiles/(?P<id>[^/]+)/$',
                            resource.Resource(handler=handlers.CompProfileHandler)),
    url(r'^0.1/json/hints/(?P<attribute>service_flavours)/$',
                            resource.Resource(handler=handlers.SuggestionHandler),
                            name='poem_external_hints'),
    url(r'^0.1/json/hints/(?P<attribute>vo)/$',
                            resource.Resource(handler=handlers.SuggestionHandler),
                            name='poem_external_hints'),
    # new API
    url(r'^0.2/(?P<emitter_format>.+)/namespace/$',
                            resource.Resource(handler=handlers.NamespaceHandler)),
    # url(r'^0.2/(?P<emitter_format>.+)/profiles/$',
    #                        resource.Resource(handler=handlers.ProfileHandler)),
    # poem-sync uses api/0.2
    url(r'^0.2/(?P<emitter_format>.+)/profiles/$',
                            resource.Resource(handler=handlers.CompProfileHandler)),
    url(r'^0.2/(?P<emitter_format>.+)/profiles/(?P<id>[^/]+)/$',
                            resource.Resource(handler=handlers.ProfileHandler)),
    url(r'^0.2/json/hints/metrics/$',
                            resource.Resource(handler=handlers.MetricHandler),
                            name='poem_metric_hints'),
    url(r'^0.2/json/hints/(?P<attribute>service_flavours)/$',
                            resource.Resource(handler=handlers.SuggestionHandler),
                            name='poem_external_hints'),
    url(r'^0.2/json/hints/(?P<attribute>vo)/$',
                            resource.Resource(handler=handlers.SuggestionHandler),
                            name='poem_external_hints'),
    url(r'^0.2/(?P<emitter_format>.+)/metrics_in_profiles/(?P<attribute>.+[^/])?$',
                            resource.Resource(handler=handlers.MetricsInProfile)),
)

