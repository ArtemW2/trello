from model_utils import FieldTracker

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import EmailValidator, MinLengthValidator

from enum import Enum

from users.services.generate_id_service import GenerateIDService

class EmployeeManager(BaseUserManager):
    def create_user(self, login, password, **extra_fields):
        if not login:
            raise ValueError("Логин обязателен")
        user = self.model(login = login, password = password, **extra_fields)
        user.set_password(password)
        user.save(using = self._db)
        return user

    def create_superuser(self, login, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        return self.create_user(login, password, **extra_fields)
    
    def authenticate(self, login=None, password=None):
        try:
            user = self.get(login=login)
            if user.check_password(password):
                return user
        except Employee.DoesNotExist:
            return None


class DepartmentChoices(Enum):
    SALES = 'Отдел продаж'
    DEVELOPMENT = 'Отдел разработки'
    # MARKETING = 'Отдел маркетинга'
    HR = 'Отдел кадров'
    # FINANCE = 'Финансовый отдел'
    # LEGAL = 'Юридический отдел'
    # LOGISTICS = 'Отдел логистики'
    ADMINISTRATION = 'Отдел системного администрирования'
    SUPPORT = 'Отдел технической поддержки'
    TESTING = "Отдел тестирования"
    SECURITY = 'Отдел безопасности'


class Department(models.Model):
    name = models.CharField(max_length = 255, choices = [(choice.value, choice.value) for choice in DepartmentChoices], verbose_name = 'Название департамента')
    department_id = models.CharField(max_length = 6, validators = [MinLengthValidator(6)], unique = True, default = GenerateIDService.generate_unique_department_id, verbose_name = 'Идентификатор департамента')

    def __str__(self):
        return f"{self.name}"


class StatusChoices(Enum):
    active = 'Работает'
    on_vacation = 'В отпуске'
    terminated = 'Уволен'


class RoleChoices(Enum):
    manager = 'Руководитель департамента'
    assistant_manager = 'Заместитель руководителя'
    support = "Сотрудник технической поддержки"
    developer = 'Разработчик'
    tester = 'Тестировщик'
    customer_manager = 'Менеджер по работе с клиентами'
    recruter = 'Рекрутер'
    admin = 'Системный администратор'
    security_guard = "Сотрудник службы безопасности"
    


class Employee(AbstractBaseUser):
    login = models.CharField(max_length = 100, db_index = True, unique = True, verbose_name = "Логин сотрудника")
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length = 100, verbose_name = 'Имя')
    last_name = models.CharField(max_length = 100, verbose_name = 'Фамилия')
    surname = models.CharField(max_length = 100, verbose_name = 'Отчество')
    date_of_birth = models.DateField(null = True, blank = True, verbose_name = 'Дата рождения')
    email = models.EmailField(max_length = 100, db_index = True, blank = True, validators = [EmailValidator], verbose_name = 'Электронная почта')
    department = models.ForeignKey(Department, on_delete = models.SET_NULL, null = True, verbose_name = 'Департамент сотрудника', related_name = 'department_employees')
    role = models.CharField(max_length = 100, null = True, blank = True, choices = [(choice.value, choice.value) for choice in RoleChoices], verbose_name = 'Роль сотрудника', default = "")
    status = models.CharField(max_length = 50, blank = True, choices = [(choice.value, choice.value) for choice in StatusChoices], verbose_name = 'Статус сотрудника', default = StatusChoices.active.value)
    hire_date= models.DateField(auto_now_add = True, verbose_name = 'Дата приема на работу')
    is_staff = models.BooleanField(default=False, verbose_name='Доступ в админку')
    termination_date = models.DateField(null = True, blank = True, verbose_name = 'Дата увольнения')
    tracker = FieldTracker(fields=['department', 'status', 'termination_date'])

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'surname']

    objects = EmployeeManager()

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.surname}"
    
    def has_perm(self, perm, obj=None):
        return True  

    def has_module_perms(self, app_label):
        return True
    

class ManagerDepartment(models.Model):
    manager = models.ForeignKey(Employee, default = "", on_delete = models.SET_DEFAULT, null = True, blank = True, verbose_name = 'Руководитель', related_name = 'manager_department')
    assistant_manager = models.ForeignKey(Employee, default = "", on_delete = models.SET_DEFAULT, verbose_name = 'Заместитель руководителя', null = True, blank = True, related_name = 'manager_department_assistant')
    department = models.ForeignKey(Department, on_delete = models.CASCADE, verbose_name = 'Департамент')
    assigned_at = models.DateField(auto_now_add = True, verbose_name = 'Дата назначения')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['manager', 'assistant_manager', 'department'],
                                    name = 'unique_manager_and_assistant_department')
        ]

    def __str__(self):
        return f"{self.department}. Руководитель - {self.manager}, заместитель - {self.assistant_manager}"
    
    
class EmployeeActionHistory(models.Model):
    executor = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.CASCADE, related_name="employee_actions")
    user = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="actions_on_employee")
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    old_value = models.CharField(max_length=255)
    new_value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.action} для {self.user} выполнено работником {self.executor}, департамент {self.executor.department}. Уникальный ID работника - {self.executor_id}"