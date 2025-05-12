from users.models import EmployeeActionHistory

class UserActionService:
    @staticmethod
    def creation(instance, executor):
        EmployeeActionHistory.objects.create(
            executor = executor,
            user = instance,
            action = "Создание учётной записи",
        )
    
    @staticmethod
    def tracked_fields_update(instance, executor):
        changes_map = {
            "department": "Изменение департамента",
            "status": "Изменение рабочего статуса",
            "termination_date": "Добавление даты увольнения",
        }
        for field, action_text in changes_map.items():
            if instance.tracker.has_changed(field):
                EmployeeActionHistory.objects.create(
                    executor=executor,
                    user=instance,
                    action=action_text,
                )