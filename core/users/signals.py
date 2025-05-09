from django.dispatch import receiver
from django.db.models.signals import post_save

from users.tasks import send_message
from users.models import ManagerDepartment, Employee
from users.services.manager_service import ManagerDepartmentService

import logging

logger = logging.getLogger(__name__)


#Отправка руководителю департамента учётных данных нового сотрудника
@receiver(post_save, sender=Employee)
def send_credentials_to_manager(sender, instance, created, **kwargs):
    if created:
        try:
            manager_department = ManagerDepartment.objects.get(department = instance.department)
            assistant_manager_email = manager_department.assistant_manager.email
            manager_email = manager_department.manager.email
            logger.info(f"Отправка письма менеджеру {manager_department.manager.last_name} {manager_department.manager.first_name} {manager_department.manager.surname} и заместителю {manager_department.assistant_manager.last_name} {manager_department.assistant_manager.first_name} {manager_department.assistant_manager.surname} о создании учётной записи для сотрудника {instance.last_name} {instance.first_name} {instance.surname}")
            send_message.delay(
                message_type='employee_created',
                context = {
                    'employee_id': instance.id,
                    'manager_email': manager_email,
                    'assistant_manager_email': assistant_manager_email,
                })
        except ManagerDepartment.DoesNotExist:
            logger.warning(f"Менеджер для департамента {instance.department} не найден")
            

###Отправка сводной информации о работниках департамента и количестве их задач 
###когда создаётся новая запись или меняется руководитель/заместитель какого-то департамента
@receiver(post_save, sender = ManagerDepartment)
def send_information_about_department_to_manager(sender, instance, created, **kwargs):
    if created:
        executors_data = ManagerDepartmentService.get_info_about_employee_tasks(department=instance.department)
        logger.info(f"В связи с новым назначением менеджера департамента, на его почту были высланы данные о работниках подразделения: {instance.manager.email}")
        send_message.delay(
            message_type="manager_is_assigned",
            context = {
                "manager_id": instance.manager.id,
                "executors_data": executors_data
            })