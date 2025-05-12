from users.models import DepartmentChoices, RoleChoices, Employee

from django.core.exceptions import ValidationError

class UserService:
    @staticmethod
    def get_queryset(user):
        if user.department.name not in ["Отдел технической поддержки", "Отдел безопасности", "Отдел кадров"]:
            return Employee.objects.filter(department=user.department)
        return Employee.objects.all()

    @staticmethod
    def assign_role_by_department(department):
        mapping = {
            DepartmentChoices.SALES.value.lower(): RoleChoices.customer_manager.value,
            DepartmentChoices.DEVELOPMENT.value.lower(): RoleChoices.developer.value,
            DepartmentChoices.HR.value.lower(): RoleChoices.recruter.value,
            DepartmentChoices.ADMINISTRATION.value.lower(): RoleChoices.admin.value,
            DepartmentChoices.SUPPORT.value.lower(): RoleChoices.support.value,
            DepartmentChoices.TESTING.value.lower(): RoleChoices.tester.value,
        }
        department_lower = department.strip().lower()

        return mapping.get(department_lower)

    @staticmethod
    def validate_data(data, user):
        if "department" in data and user.department.name != "Отдел технической поддержки":
            raise ValidationError(f"Вы не можете изменить данное поле")
        
        return data

    @staticmethod
    def prepare_data_for_create(data):
        data["role"] = UserService.assign_role_by_department(data["department"].name)

        return data
    
    @staticmethod
    def prepare_data_for_update(data, instance):
        department = data.get("department")
        
        if department and department != instance.department:
            instance.department = department
            instance.role = UserService.assign_role_by_department(instance.department.name)
        
        return instance