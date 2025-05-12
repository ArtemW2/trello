from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models import Case, When, Value

from core.user_middleware import get_current_user

from users.tasks import send_message
from users.models import ManagerDepartment, Employee
from users.services.manager_service import ManagerDepartmentService
from users.services.user_service import UserService
from users.services.user_action_service import UserActionService

import logging

logger = logging.getLogger(__name__)


"Отправка руководителю департамента учётных данных нового сотрудника"
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
        except Exception as e:
            logger.error(f"Ошибка отправки письма: {e}")
            

"""Отправка сводной информации о работниках департамента и количестве их задач
когда создаётся новая запись или меняется руководитель/заместитель какого-то департамента"""
@receiver(post_save, sender = ManagerDepartment)
def send_information_about_department_to_manager(sender, instance, created, **kwargs):
    if created:
        executors_data = ManagerDepartmentService.get_info_about_employee_tasks(department=instance.department)
        logger.info(f"В связи с новым назначением менеджера департамента, на его почту были высланы данные о работниках подразделения: {instance.manager.email}")
        try:
            send_message.delay(
            message_type="manager_is_assigned",
            context = {
                "manager_id": instance.manager.id,
                "executors_data": executors_data
            })
        except Exception as e:
            logger.error(f"Ошибка отправки письма: {e}")
        

"""При создании/обновлении записи в таблице Менеджеров департаментов, обновляются роли для новоназначенных сотрудников на должности.
Для сотрудника, который перестал занимать какую-либо должность возвращается дефолтная роль для департамента"""
@receiver(post_save, sender = ManagerDepartment)
def update_employee_role(sender, instance, created, **kwargs):
    Employee.objects.filter(id__in=[instance.manager.id, instance.assistant_manager.id]).update(role=Case(
            When(id=instance.manager.id, then=Value('Руководитель департамента')),
            When(id=instance.assistant_manager.id, then=Value("Заместитель руководителя"))
        )
    )
    role = UserService.assign_role_by_department(instance.department.name)
    Employee.objects.filter(department=instance.department, role__in=['Руководитель департамента',"Заместитель руководителя"]).exclude(id__in=[instance.manager.id, instance.assistant_manager.id]).update(role=role)


"Записи о создании учёток, изменении департамента/статуса/даты увольнения добавляются в таблицу действий над пользователями"
@receiver(post_save, sender = Employee)
def log_employee_action(sender, instance, created, **kwargs):
    executor = get_current_user()
    "Заглушка для тестов"
    if not isinstance(executor, Employee) or not Employee.objects.filter(pk=getattr(executor, 'pk', None)).exists():
        return
    if created:
        UserActionService.creation(instance, executor)
    else:
        UserActionService.tracked_fields_update(instance, executor)


@receiver(post_save, sender = ManagerDepartment)
def log_manager_department(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Менеджер {instance.manager} назначен руководителем департамента {instance.department}")
    else:
        logger.info(f"Назначен новый менеджер для департамента {instance.department}. Теперь его возглавляет {instance.manager}")
        