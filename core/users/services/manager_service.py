from users.models import Employee
from django.db.models import Q, Count

"""Информация по количеству активных задач каждого работника департамента"""
class ManagerDepartmentService:
    @staticmethod
    def get_info_about_employee_tasks(department):
        executors = Employee.objects.filter(department = department).annotate(
            active_tasks_count = Count('executed_tasks', filter = Q(executed_tasks__status__in = ['open', 'in_progress', 'on_review']))
        )

        executors_data = []

        for executor in executors:
            executors_data.append({
                'ФИО работника': f"{executor.last_name} {executor.first_name} {executor.surname}",
                "Количество активных задач": executor.active_tasks_count
            })

        return executors_data