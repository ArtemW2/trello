# Generated by Django 5.1.7 on 2025-04-01 09:06

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Metrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.DateField(default=django.utils.timezone.now)),
                ('solved_tasks_percentage', models.FloatField(default=0.0)),
                ('active_tasks_count', models.PositiveIntegerField(default=0)),
                ('overdue_tasks_percentage', models.FloatField(default=0.0)),
                ('bonus_coefficient', models.FloatField(default=1.0, verbose_name='Бонусный коэффициент')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('employee', 'month'), name='employee_productivity_monthly')],
            },
        ),
    ]
