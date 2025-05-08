from celery import shared_task

from users.services.notification_service import NotificationManagerService
from users.models import Employee
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_message(message_type, context):
    if "employee_id" in context:
        try:
            employee = Employee.objects.get(id=context["employee_id"])
            context.update({
                "last_name": employee.last_name,
                "first_name": employee.first_name,
                "surname": employee.surname,
                "login": employee.login,
                "password": employee.password,
            })
        except Employee.DoesNotExist:
            logger.error(f"Пользователь не найден")
            return
    if "manager_id" in context:
        try:
            manager = Employee.objects.get(id=context['manager_id'])
            context.update({
                    "first_name": manager.first_name,
                    "surname": manager.surname,
                    "manager_email": manager.email,
                })
        except Employee.DoesNotExist:
            logger.error(f"Mенеджер не найден")
            return
    NotificationManagerService.send_notification(message_type, context)

