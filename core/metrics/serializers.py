from rest_framework import serializers

from metrics.models import Metrics

class MetricsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Metrics
        fields = '__all__'