from django.contrib import admin
from django.conf.urls import url
from Poem.poem import views

admin.autodiscover()

urlpatterns = [
    url(r'^0.2/json/profiles/?$', views.Profiles.as_view()),
    url(r'^0.2/json/metrics_in_profiles/?$', views.MetricsInProfiles.as_view()),
    url(r'^0.2/json/metrics_in_group/?$', views.MetricsInGroup.as_view()),
    url(r'^0.2/json/metrics/?$', views.Metrics.as_view())
]
