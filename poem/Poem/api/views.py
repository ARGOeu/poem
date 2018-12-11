from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from . import serializers

from Poem.poem import models

class ListProfile(generics.ListAPIView):
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileSerializer

class DetailProfile(generics.RetrieveAPIView):
    lookup_field = 'name'
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
