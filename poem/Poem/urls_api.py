from django.conf.urls.defaults import patterns, url

from Poem.poem import views

urlpatterns = patterns('Poem.poem.views',
    url(r'^0.1/json/hints/service_flavours$','hints_service_flavours'),
    url(r'^0.1/json/hints/vo$', 'hints_vo'),
    url(r'^0.1/json/hints/metrics$', 'hints_metrics'),
    url(r'^0.2/json/profiles$', 'profiles'),
    url(r'^0.2/json/metrics_in_profiles$', 'metrics_in_profiles')
)
