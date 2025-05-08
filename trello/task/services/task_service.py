from django.db.models import Q
from django.core.exceptions import ValidationError

from task.models import Task, TaskHistory
from users.models import DepartmentChoices, ManagerDepartment

import logging

logger = logging.getLogger(__name__)


class TaskService:
    """
    Техническая поддержка получает список всех задач, остальные только те, в которых участвуют
    """
    @staticmethod
    def get_queryset(user):
        logger.info(f"Пользователь {user} пытается получить данные по задачам")
        if hasattr(user, 'department') and user.department and user.department.name == DepartmentChoices.SUPPORT.value:
            return Task.objects.all()
        if ManagerDepartment.objects.filter(Q(manager=user) | Q(assistant_manager=user)).exists():
            return Task.objects.filter(Q(author = user) | Q(executors=user) | Q(department=user.department))
        else:
            return Task.objects.filter(Q(author=user) | Q(executors=user)).distinct()
    

    """
    Менять название задачи или её описание может только автор
    Назначать сотрудника на задачу, если задача закреплена за департаментом, к которому сотрудник не имеет отношения, нельзя
    Приоритет, назначать департамент и исполнителей может только техническая поддержка(ещё думаю)
    """
    @staticmethod
    def validate_data(data, instance, context_user):
        user = context_user
        if instance:
            department = data.get("department", instance.department)
            if any(key in data for key in ['text', 'title']):
                if user != instance.author:
                    raise ValidationError("Только автор задачи может изменить текст задачи или ее название")
        else:
            department = data.get("department")

        executors = data.get("executors", [])

        for executor in executors:
            if executor.department.id != department.id:
                raise ValidationError("На задачу не может быть назначен сотрудник из другого департамента")

        if any(key in data for key in ['priority', 'department', 'executors']):
            if user.department.name != 'Отдел технической поддержки':
                raise ValidationError("Вы не можете изменить приоритет задачи/назначить ответственный департамент/назначить исполнителя")

        return data
    


    """
    Если изменяется только департамент, то очищаем список исполнителей
    Если департамент остаётся прежним, а исполнители добавляются, то добавляем их в список текущих исполнителей
    """
    @staticmethod
    def prepare_update_data(instance, validated_data):
        department = validated_data.get("department", instance.department)
        
        if department is not None and department != instance.department:
            instance.executors.clear()
        
        instance.department = department

        executors = validated_data.pop("executors", None)

        if executors is not None:
            instance.executors.add(*executors)

        if instance.executors.exists():
            instance.status = "in_progress"

        instance.save()

        return validated_data
    

    """
    Даже если в запросе при создании задачи будут переданы исполнители, департамент или приоритет, данные будут выкинуты из запроса 
    """
    @staticmethod
    def prepare_create_data(data, context_user):
        data['author'] = context_user

        executors = data.pop("executors", None)
        department = data.pop("department", None)
        priority = data.pop("priority", None)

        return data
        

class TaskHistoryService:
    """
    Техническая поддержка видит все действия по всем задачам, остальные только по тем, в каких участвуют
    """
    @staticmethod
    def get_queryset(user):
        logger.info(f"Пользователь {user} пытается получить данные по задачам")
        if hasattr(user, 'department') and user.department and user.department.name == DepartmentChoices.SUPPORT.value:
            return TaskHistory.objects.all()
        if ManagerDepartment.objects.filter(Q(manager=user) | Q(assistant_manager=user)).exists():
            return TaskHistory.objects.filter(Q(task__author=user) | Q(task__executors=user) | Q(task__department=user.department))
        else:
            return TaskHistory.objects.filter(Q(task__executors=user) | Q(task__author=user)).distinct()