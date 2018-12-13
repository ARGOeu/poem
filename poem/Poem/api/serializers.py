from rest_framework import serializers

from Poem.poem import models


class MetricInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MetricInstance
        fields = ('service_flavour', 'metric')


class ProfileSerializer(serializers.ModelSerializer):
    metric_instances = MetricInstanceSerializer(many=True, read_only=True)

    class Meta:
        fields = (
            'name',
            'vo',
            'description',
            'metric_instances'
        )
        model = models.Profile
