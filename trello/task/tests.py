import io

from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

# Create your tests here.
from task.models import *
from users.models import Department, Employee
from users.services.auth_service import AuthService

class TaskViewSetTests(APITestCase):
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
        
        self.developer_task = Task.objects.create(
            title = "Создание департамента",
            text = "Необходимо добавить информацию по новому департаменту: ",
            author = self.employee,
        )

        self.support_task = Task.objects.create(
            title = "Назначение менеджера",
            text = "В департаменте 'Отдел технической поддержки' назначен новый менеджер. Обновите информацию ",
            author = self.support_employee,
        )
       
        support_tokens = AuthService.generate_tokens(self.support_employee)
        develop_tokens = AuthService.generate_tokens(self.employee)
        self.access_develop_token = develop_tokens["access"]
        self.access_support_token = support_tokens["access"]

    def test_create_task_by_employee(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + self.access_develop_token)
        url = reverse("tasks-list")
        data = {
            "author": self.employee.id,
            "title": "Внесений изменений в отчёт",
            "text": "Необходимо внести следующие корректировки: "
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_task_information_by_member_task(self):
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_develop_token)
        data = {
            "title": "Создание департамента(TEST)",
            "text": "Тестовая запись"
        }
        url = reverse("tasks-detail", args=[self.developer_task.id])
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_another_task_information_by_not_member_task_and_not_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_develop_token)
        data = {
            "title": "Создание департамента(TEST)",
            "text": "Тестовая запись"
        }
        url = reverse("tasks-detail", args=[self.support_task.id])
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_another_task_information_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_support_token)
        data = {
            "title": "Создание департамента(TEST)",
            "text": "Тестовая запись"
        }
        url = reverse("tasks-detail", args=[self.developer_task.id])
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_attach_file_to_task(self):
        file_content = b'Test file content'
        file = io.BytesIO(file_content)
        file.name = "test_file.txt"
        
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_support_token)
        url = reverse("tasks-upload-files", args=[self.developer_task.id])
        data = {
            "files": [file],
        }
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)