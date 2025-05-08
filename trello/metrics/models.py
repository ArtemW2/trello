from django.db import models
from django.utils import timezone

from users.models import Employee


class Metrics(models.Model):
    employee = models.ForeignKey(Employee, on_delete = models.CASCADE)
    month = models.DateField(default = timezone.now)
    solved_tasks_percentage = models.FloatField(default = 0.0)
    active_tasks_count = models.PositiveIntegerField(default = 0)
    overdue_tasks_percentage = models.FloatField(default = 0.0)
    bonus_coefficient = models.FloatField(default=1.0, verbose_name='Бонусный коэффициент')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['employee', 'month'],
                                    name = 'employee_productivity_monthly')
        ]
