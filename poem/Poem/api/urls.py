from django.urls import path

from . import views

urlpatterns = [
    path('profiles/', views.ListProfile.as_view()),
    path('profiles/<str:name>/', views.DetailProfile.as_view()),
    path('metrics/', views.ListMetrics.as_view()),
    path('metrics/<str:tag>', views.ListTaggedMetrics.as_view())
]
