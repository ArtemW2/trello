# Generated by Django 5.1.7 on 2025-05-03 02:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_remove_employee_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='must_change_password',
            field=models.BooleanField(default=True),
        ),
    ]
