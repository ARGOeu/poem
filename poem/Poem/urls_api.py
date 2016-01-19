from django.contrib import admin
from django.conf.urls import patterns, url, include
from ajax_select import urls as ajax_select_urls
from Poem.poem import views

admin.autodiscover()

urlpatterns = patterns('Poem.poem.views',
    url(r'^0.2/json/profiles$', 'profiles'),
    url(r'^0.2/json/metrics_in_profiles$', 'metrics_in_profiles')
)
