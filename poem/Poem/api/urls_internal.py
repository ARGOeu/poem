from django.urls import path

from . import views_internal

urlpatterns = [
    path('metrics/<str:group>', views_internal.ListMetricsInGroup.as_view()),
    path('tokens/', views_internal.ListTokens.as_view()),
    path('tokens/<str:name>', views_internal.ListTokenForTenant.as_view()),
]

