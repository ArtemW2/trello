from django.urls import reverse
from unittest.mock import patch

from rest_framework.test import APITestCase
from rest_framework import status

from users.serializers import *
from users.models import *
from users.services.auth_service import AuthService


class BaseSetUp(APITestCase):
    def setUp(self):
        self.support_department = Department.objects.create(
            name="Отдел технической поддержки"
        )
        self.developer_department = Department.objects.create(
            name="Отдел разработки"
        )
        self.security_department = Department.objects.create(
            name="Отдел безопасности"
        )
        self.hr_department = Department.objects.create(
            name="Отдел кадров"
        )
        self.developer = Employee.objects.create(
            login="developer_user",
            password="strongpassword123",
            first_name="Разраб",
            last_name="Разраб",
            surname="Разраб",
            email="ivan@example.com",
            department=self.developer_department,
        )
        self.second_developer = Employee.objects.create(
            login="developer2_user",
            password="strongpassword123",
            first_name="Разраб2",
            last_name="Разраб2",
            surname="Разраб2",
            email="ivan@example.com",
            department=self.developer_department,
        )
        self.support = Employee.objects.create(
            login="support_user",
            password="strongpassword123",
            first_name="Саппорт",
            last_name="Саппорт",
            surname="Саппорт",
            email="ivan@example.com",
            department=self.support_department,
        )
        self.second_support = Employee.objects.create(
            login="support2_user",
            password="strongpassword123",
            first_name="Саппорт2",
            last_name="Саппорт2",
            surname="Саппорт2",
            email="ivan@example.com",
            department=self.support_department,
        )
        self.security = Employee.objects.create(
            login="security_user",
            password="strongpassword123",
            first_name="СБ",
            last_name="СБ",
            surname="СБ",
            email="ivan@example.com",
            department=self.security_department,
        )
        self.hr = Employee.objects.create(
            login="hr_user",
            password="strongpassword123",
            first_name="HR",
            last_name="HR",
            surname="HR",
            email="ivan@example.com",
            department=self.hr_department,
        )
        self.manager_support_department = ManagerDepartment.objects.create(
            manager=self.support,
            assistant_manager=self.second_support,
            department=self.support_department
        )
        self.access_develop_token = AuthService.generate_tokens(self.developer)["access"]
        self.access_second_develop_token = AuthService.generate_tokens(self.second_developer)["access"]
        self.access_support_token = AuthService.generate_tokens(self.support)["access"]
        self.access_second_support_token = AuthService.generate_tokens(self.second_support)["access"]
        self.access_security_token = AuthService.generate_tokens(self.security)["access"]
        self.access_hr_token = AuthService.generate_tokens(self.hr)["access"]


class EmployeeViewSetTests(BaseSetUp):
    "Сотрудники из департаментов Отдел технической поддержки, Отдел безопасности, Отдел HR имеют доступ ко всему списку"
    def test_get_all_queryset_by_permitted_departments(self):
        tokens = [self.access_support_token, self.access_security_token, self.access_hr_token]
        url = reverse("employee-list")
        for token in tokens:
            self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {token}")
            response = self.client.get(url)
            data = response.json()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(data), Employee.objects.count())

    "Сотрудники других департаментов видят только сотрудников своего департамента"
    def test_get_limited_queryset_by_other_departments(self):
        url = reverse("employee-list")
        self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {self.access_develop_token}" )
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), Employee.objects.filter(department=self.developer_department).count())

    def test_update_user_info_by_support_or_owner(self):
        tokens = [self.access_support_token, self.access_develop_token]
        url = reverse("employee-detail", args=[self.developer.id])
        data = {
            "login": "123"
        }
        for token in tokens:
            self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {token}")
            response = self.client.patch(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["login"], "123")

    def test_update_user_info_by_not_support_and_owner(self):
        tokens = [self.access_security_token, self.access_hr_token]
        url = reverse("employee-detail", args=[self.developer.id])
        data = {
            "login": "123"
        }
        for token in tokens:
            self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {token}")
            response = self.client.patch(url, data)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_user_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_support_token)
        data = {
            "login":"test",
            "password":"strongpassword123",
            "first_name":"СБ",
            "last_name":"СБ",
            "surname":"СБ",
            "email":"test@mail.ru",
            "department": self.security_department.id
        }
        url = reverse("employee-list")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_by_other_departments(self):
        tokens = [self.access_develop_token, self.access_security_token, self.access_hr_token]
        data = {
            "login":"test",
            "password":"strongpassword123",
            "first_name":"СБ",
            "last_name":"СБ",
            "surname":"СБ",
            "email":"test@mail.ru",
            "department": self.security_department.id
        }
        url = reverse("employee-list")
        for token in tokens:
            self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {token}")
            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_support_token)
        url = reverse("employee-detail", args=[self.support.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_user_by_other_departments(self):
        tokens = [self.access_develop_token, self.access_security_token, self.access_hr_token]
        url = reverse("employee-detail", args=[self.support.id])
        for token in tokens:
            self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {token}")
            response = self.client.delete(url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DepartmentViewSetTests(BaseSetUp):

    def test_get_queryset_departments(self):
        tokens = [self.access_develop_token, self.access_hr_token, self.access_security_token, self.access_support_token]
        url = reverse("department-list")
        for token in tokens:
            self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {token}")
            response = self.client.get(url)
            data = response.json()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(data), Department.objects.count())

    def test_update_department_info_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {self.access_support_token}")
        url = reverse("department-detail", args=[self.support_department.id])
        data = {
            "name": "Отдел продаж"
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_update_department_info_by_other_departments(self):
        tokens = [self.access_develop_token, self.access_hr_token, self.access_security_token]
        url = reverse("department-detail", args=[self.support_department.id])
        data = {
            "name": "Отдел продаж"
        }
        for token in tokens:
            self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {token}")
            response = self.client.patch(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_department_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {self.access_support_token}")
        url = reverse("department-detail", args=[self.support_department.id])
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_department_by_other_departments(self):
        tokens = [self.access_develop_token, self.access_hr_token, self.access_security_token]
        url = reverse("department-detail", args=[self.support_department.id])
        for token in tokens:
            self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {token}")
            response = self.client.delete(url, format="json")
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ManagerDepartmentViewSetTests(BaseSetUp):
    
    def test_assign_manager_department_by_support_is_failure(self):
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_support_token)
        data = {
            "manager": self.support.id,
            "assistant_manager": self.developer.id, #Department differs from assigned
            "department": self.support_department.id
        }
        url = reverse("manager-list")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_manager_department_by_support_succesfully(self):
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_support_token)
        data = {
            "manager": self.developer.id,
            "assistant_manager": self.second_developer.id,
            "department": self.developer_department.id
        }
        url = reverse("manager-list")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_assign_manager_department_by_other_departments(self):
        tokens = [self.access_develop_token, self.access_security_token, self.access_hr_token]
        data = {
            "manager": self.support.id,
            "assistant_manager": self.second_support.id,
            "department": self.support_department.id
        }
        url = reverse("manager-list")
        for token in tokens:
            self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {token}")
            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_queryset(self):
        tokens = [self.access_develop_token, self.access_hr_token, self.access_security_token, self.access_support_token]
        url = reverse("manager-list")
        for token in tokens:
            self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {token}")
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_manager_department_info_by_support_successfully(self):
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_support_token)
        data = {
            "manager": self.second_support.id,
            "assistant_manager": self.support.id, 
            "department": self.support_department.id
        }
        url = reverse("manager-detail", args=[self.manager_support_department.id])
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_manager_department_info_by_support_failure(self):
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_support_token)
        data = {
            "manager": self.second_support.id,
            "assistant_manager": self.developer.id, 
            "department": self.support_department.id
        }
        url = reverse("manager-detail", args=[self.manager_support_department.id])
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_manager_department_info_by_other_departments(self):
        tokens = [self.access_develop_token, self.access_hr_token, self.access_security_token]
        data = {
            "manager": self.second_support.id,
            "assistant_manager": self.support.id, 
            "department": self.support_department.id
        }
        url = reverse("manager-detail", args=[self.manager_support_department.id])
        for token in tokens:
            self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {token}")
            response = self.client.patch(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_list_info_about_department_employees_by_manager_or_assistant(self):
        tokens = [self.access_second_support_token, self.access_second_support_token]
        url = reverse("manager-get-info-about-executors", args=[self.manager_support_department.id])
        for token in tokens:
            self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {token}")
            response = self.client.get(url)
            data = response.json()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(data), Employee.objects.filter(department=self.support_department).count())
            
    def test_get_list_info_about_department_employees_by_not_a_manager_or_assistant(self):
        tokens = [self.access_security_token, self.access_develop_token, self.access_hr_token]
        url = reverse("manager-get-info-about-executors", args=[self.manager_support_department.id])
        for token in tokens:
            self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {token}")
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    