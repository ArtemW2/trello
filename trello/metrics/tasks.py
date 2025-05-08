from django.utils import timezone

from celery import shared_task

from metrics.services.metrics_service import MetricService
from users.models import Employee


@shared_task
def update_metrics_daily():
    current_month = timezone.now().date().replace(day=1)
    for employee in Employee.objects.all():
        MetricService.update_metrics_for_employee(employee, current_month)