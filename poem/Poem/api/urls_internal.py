from django.urls import path

from . import views_internal

urlpatterns = [
    path('metrics/<str:group>', views_internal.ListMetricsInGroup.as_view()),
    path('tokens/', views_internal.ListTokens.as_view()),
    path('tokens/<str:name>', views_internal.ListTokenForTenant.as_view()),
    path('users/', views_internal.ListUsers.as_view()),
    path('groups/', views_internal.ListGroupsForUser.as_view()),
    path('groups/<str:group>', views_internal.ListGroupsForUser.as_view()),
    path('probes/<str:probe_name>', views_internal.ListProbes.as_view()),
    path('aggregations/', views_internal.ListAggregations.as_view()),
    path('aggregations/<str:aggregation_name>', views_internal.ListAggregations.as_view()),
]
