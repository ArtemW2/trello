from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from metrics.models import Metrics
from metrics.serializers import MetricsSerializers


class MetricsViewSet(ModelViewSet):
    queryset = Metrics.objects.all()
    serializer_class = MetricsSerializers
    permission_classes = (IsAuthenticated,)


