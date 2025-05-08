from django.db.models import Count, Q
from django.utils import timezone

from metrics.models import Metrics

from task.models import Task

class MetricService:
    @staticmethod
    def update_metrics_for_employee(employee, month):
        task = Task.objects.filter(executors = employee).aggregate(
            total_tasks = Count('id'),
            solved_tasks = Count('id', filter = Q(status='closed')),
            overdue_tasks = Count('id', filter = Q(deadline__lt = timezone.now().date())),
            active_tasks = Count('id', filter=Q(status__in = ['open', 'in_progress', 'on_review']))
        )

        total_tasks = task['total_tasks']
        solved_tasks = task['solved_tasks']
        overdue_tasks = task['overdue_tasks']
        active_tasks = task['active_tasks']

        solved_tasks_percentage = solved_tasks / total_tasks * 100 if total_tasks > 0 else 0
        active_tasks_count = active_tasks
        overdue_tasks_percentage = overdue_tasks / active_tasks * 100 if total_tasks > 0 else 0
        bonus_coefficient = 1 + (solved_tasks_percentage * 0.01) - (overdue_tasks_percentage * 0.02)

        metrics, created = Metrics.objects.get_or_create(
            employee = employee,
            month = month
        )

        metrics.solved_tasks_percentage = solved_tasks_percentage
        metrics.active_tasks_count = active_tasks_count
        metrics.overdue_tasks_percentage = overdue_tasks_percentage
        metrics.bonus_coefficient = bonus_coefficient

        metrics.save()