from django.urls import path

from . import views_internal

urlpatterns = [
    path('metrics/<str:group>', views_internal.ListMetricsInGroup.as_view()),
]

