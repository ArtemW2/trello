from django.urls import reverse
from django.test import TestCase

from unittest.mock import patch

from rest_framework.test import APITestCase
from rest_framework import status

from users.serializers import *
from users.models import *
from users.services.auth_service import AuthService


class EmployeeViewSetTests(APITestCase):
    def setUp(self):
        support_department = Department.objects.create(
            name = "Отдел технической поддержки",
        )
        department = Department.objects.create(
            name = "Отдел разработки",
        )

        self.employee = Employee.objects.create(
            login = "default_user",
            password = "strongpassword123",
            first_name = "Разраб",
            last_name = "Разраб",
            surname = "Разраб",
            email =  "ivan@example.com",
            department = department,
            role = "Разработчик",
            status = "Работает"
        )
        self.support_employee = Employee.objects.create(
            login =  "support_user",
            password = "strongpassword123",
            first_name = "Саппорт",
            last_name = "Саппорт",
            surname = "Саппорт",
            email =  "ivan@example.com",
            department = support_department,
            role = "Саппорт",
            status = "Работает"
            )
       
        support_tokens = AuthService.generate_tokens(self.support_employee)
        develop_tokens = AuthService.generate_tokens(self.employee)
        self.access_develop_token = develop_tokens["access"]
        self.access_support_token = support_tokens["access"]

    def test_create_employee_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + self.access_support_token)
        data = {
            'login': 'brbrbr',
            'first_name': 'Петр',
            'password': "1234",
            'last_name': 'Петров',
            'surname': 'Петрович',
            'email': 'petr@example.com',
            'department': self.support_employee.department.id,
            "role": "Разработчик",
            "status": "Работает"
        }
        url = reverse("employee-list")
        response = self.client.post(url, data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #Изменить логику, самого себя удалять нельзя
    def test_delete_yourself_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_support_token)
        url = reverse("employee-detail", args = [self.support_employee.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_another_employee_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_support_token)
        url = reverse('employee-detail', args = [self.employee.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_list_employees_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_support_token)
        url = reverse("employee-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_personal_information_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_support_token)
        url = reverse("employee-detail", args=[self.support_employee.id])
        data = {
            "first_name": "Саппорт 1"
        }
        response = self.client.patch(url, data, format = "json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_personal_information_about_another_employee_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_support_token)
        url = reverse("employee-detail", args=[self.employee.id])
        data = {
            "first_name": "Разработчик 22"
        }
        self.employee.refresh_from_db()
        print(self.employee.first_name)
        response = self.client.patch(url, data, format = "json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)  

    def test_create_employee_by_developer(self):
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_develop_token)
        data = {
            'login': 'brbrbr1',
            'first_name': 'Петр',
            'password': "1234",
            'last_name': 'Петров',
            'surname': 'Петрович',
            'email': 'petr@example.com',
            'department': self.support_employee.department.id,
            "role": "Разработчик",
            "status": "Работает"
        }
        url = reverse("employee-list")
        response = self.client.post(url, data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_yourself_by_developer(self):
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_develop_token)
        url = reverse("employee-detail", args = [self.employee.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_another_employee_by_developer(self):
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_develop_token)
        url = reverse("employee-detail", args = [self.support_employee.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_list_employees_by_developer(self):
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_develop_token)
        url = reverse("employee-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_personal_information_by_developer(self):
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_develop_token)
        url = reverse("employee-detail", args=[self.employee.id])
        data = {
            "first_name": "Разработчик 1"
        }
        response = self.client.patch(url, data, format = "json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)  

    def test_update_personal_information_about_another_employee_by_developer(self):

        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_develop_token)
        url = reverse("employee-detail", args=[self.support_employee.id])
        data = {
            "first_name": "Саппорт 22"
        }
        self.support_employee.refresh_from_db()
        print(self.support_employee.first_name)
        response = self.client.patch(url, data, format = "json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  


class DepartmentViewSetTests(APITestCase):
    def setUp(self):
        self.support_department = Department.objects.create(
            name = "Отдел технической поддержки",
        )
        self.department = Department.objects.create(
            name = "Отдел разработки",
        )

        self.employee = Employee.objects.create(
            login = "default_user",
            password = "strongpassword123",
            first_name = "Разраб",
            last_name = "Разраб",
            surname = "Разраб",
            email =  "ivan@example.com",
            department = self.department,
            role = "Разработчик",
            status = "Работает"
        )
        self.support_employee = Employee.objects.create(
            login =  "support_user",
            password = "strongpassword123",
            first_name = "Саппорт",
            last_name = "Саппорт",
            surname = "Саппорт",
            email =  "ivan@example.com",
            department = self.support_department,
            role = "Саппорт",
            status = "Работает"
            )
       
        support_tokens = AuthService.generate_tokens(self.support_employee)
        develop_tokens = AuthService.generate_tokens(self.employee)
        self.access_develop_token = develop_tokens["access"]
        self.access_support_token = support_tokens["access"]
    
    def test_create_department_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + self.access_support_token)
        data = {
            "name": "Отдел продаж",

        }
        url = reverse("department-list")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_department_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + self.access_support_token)
        url = reverse("department-detail", args = [self.department.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_list_department_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + self.access_support_token)
        url = reverse("department-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    #Статус 400 срабатывает из-за того что name не использует значение из списка DepartmentChoices, любое значение оттуда приведёт к статусу 200
    def test_update_info_about_department_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + self.access_support_token)
        url = reverse("department-detail", args = [self.department.id])
        data = {
            "name": "Отдел программистов"
        }
        response = self.client.patch(url, data, format="json")
        self.department.refresh_from_db()
        print(self.department.name)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_department_by_developer(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + self.access_develop_token)
        data = {
            "name": "Отдел ошибочного тестирования",
        
        }
        url = reverse("department-list")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_department_by_developer(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + self.access_develop_token)
        url = reverse("department-detail", args = [self.department.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_list_department_by_developer(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + self.access_develop_token)
        url = reverse("department-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_info_about_department_by_developer(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + self.access_develop_token)
        url = reverse("department-detail", args=[self.department.id])
        data = {
            "name": "Финансовый отдел"
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ManagerDepartmentViewSetTests(APITestCase):
    def setUp(self):
        self.support_department = Department.objects.create(
            name = "Отдел технической поддержки",
        )

        self.department = Department.objects.create(
            name = "Отдел разработки",
        )

        self.support_employee = Employee.objects.create(
            login =  "support_user",
            password = "strongpassword123",
            first_name = "Саппорт",
            last_name = "Саппорт",
            surname = "Саппорт",
            email =  "support@example.com",
            department = self.support_department,
            role = "Саппорт",
            status = "Работает"
            )
        
        self.employee = Employee.objects.create(
            login = "default_user",
            password = "strongpassword123",
            first_name = "Разраб",
            last_name = "Разраб",
            surname = "Разраб",
            email =  "developer@example.com",
            department = self.department,
            role = "Разработчик",
            status = "Работает"
        )

        self.manager = Employee.objects.create(
            login = "manager_user",
            password = "strongpassword123",
            first_name = "Менеджер",
            last_name = "Менеджер",
            surname = "Менеджер",
            email =  "manager@example.com",
            department = self.department,
            role = "Менеджер",
            status = "Работает"
        )

        self.assistant_manager = Employee.objects.create(
            login = "assistant_manager_user",
            password = "strongpassword123",
            first_name = "Заместитель Менеджера",
            last_name = "Заместитель Менеджера",
            surname = "Заместитель Менеджера",
            email =  "manager@example.com",
            department = self.department,
            role = "Заместитель Менеджера",
            status = "Работает"
        )

        self.manager_department = ManagerDepartment.objects.create(
            manager = self.manager,
            assistant_manager = self.assistant_manager,
            department = self.department
        )

        support_tokens = AuthService.generate_tokens(self.support_employee)
        develop_tokens = AuthService.generate_tokens(self.employee)
        manager_tokens = AuthService.generate_tokens(self.manager)
        assistant_manager_tokens = AuthService.generate_tokens(self.assistant_manager)
        self.access_develop_token = develop_tokens["access"]
        self.access_support_token = support_tokens["access"]
        self.access_manager_token = manager_tokens["access"]
        self.access_assistant_manager_token = assistant_manager_tokens["access"]

    #Сотрудник другого департамента не может быть назначен менеджером
    def test_assign_employee_to_department_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + self.access_support_token)
        url = reverse("manager-list")
        data = {
            "manager": self.employee.id,
            "assistant_manager": self.support_employee.id,
            "department": self.support_department.id,
        }
        response = self.client.post(url, data, format="json")
        self.manager_department.refresh_from_db()
        print(self.manager_department)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_information_about_manager_department_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + self.access_support_token)
        url = reverse("manager-detail", args=[self.manager_department.id])
        data = {
            "manager": self.employee.id,
            "department": self.department.id
        }
        response = self.client.patch(url, data, format="json")
        self.manager_department.refresh_from_db()
        print(self.manager_department)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_info_about_executor_tasks_department_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + self.access_support_token)
        url = reverse("manager-get-info-about-executors", args=[self.manager_department.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_note_about_manager_department_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + self.access_support_token)
        url = reverse("manager-detail", args=[self.manager_department.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_list_manager_department_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + self.access_support_token)
        url = reverse("manager-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_assign_employee_to_department_by_developer(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + self.access_develop_token)
        url = reverse("manager-list")
        data = {
            "manager": self.employee.id,
            "assistant_manager": self.support_employee.id,
            "department": self.support_department.id,
        }
        response = self.client.post(url, data, format="json")
        self.manager_department.refresh_from_db()
        print(self.manager_department)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_information_about_manager_department_by_developer(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + self.access_develop_token)
        url = reverse("manager-detail", args=[self.manager_department.id])
        data = {
            "manager": self.employee.id,
            "department": self.department.id
        }
        response = self.client.patch(url, data, format="json")
        self.manager_department.refresh_from_db()
        print(self.manager_department)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_info_about_executor_tasks_department_by_developer(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + self.access_develop_token)
        url = reverse("manager-get-info-about-executors", args=[self.manager_department.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_note_about_manager_department_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + self.access_develop_token)
        url = reverse("manager-detail", args=[self.manager_department.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_list_manager_department_by_developer(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + self.access_develop_token)
        url = reverse("manager-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_info_about_executor_tasks_department_by_manager(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + self.access_manager_token)
        url = reverse("manager-get-info-about-executors", args=[self.manager_department.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_info_about_executor_tasks_department_by_assistant_manager(self):


        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + self.access_assistant_manager_token)
        url = reverse("manager-get-info-about-executors", args=[self.manager_department.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

