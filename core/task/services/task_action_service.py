from task.models import TaskHistory
from users.models import Employee

class TaskHistoryService:
    @staticmethod
    def creation(instance):
        TaskHistory.objects.create(
            task = instance,
            employee = instance.author,
            action = f"Создание задачи",
            new_value = instance.title
        )

    @staticmethod
    def tracked_fields_change(instance):
        changes_map = {
            "status": "Изменение приоритета задачи",
            "priority": "Изменение приоритета задачи"
        }
        for field, action_text in changes_map.items():
            if instance.tracker.has_changed(field):
                TaskHistory.objects.create(
                    task = instance,
                    employee = None,
                    action = action_text,
                    old_value = instance.tracker.previous("status"),
                    new_value = instance.status
                )

    @staticmethod
    def update_executors_list(instance, pk_set, user):
        added_executors = Employee.objects.filter(pk__in = pk_set)
        TaskHistory.objects.create(
            task = instance,
            employee = user,
            action = 'Назначение исполнителя',
            new_value = ', '.join(f"{executor.last_name} {executor.first_name} {executor.surname}" for executor in added_executors)
        )