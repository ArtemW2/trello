import io

from django.db.models import Q
from django.urls import reverse

from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase


from task.models import Task, TaskHistory
from users.models import Department, Employee


from users.services.auth_service import AuthService


class TaskViewSetBaseSetUp(APITestCase):
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
        self.developer_task = Task.objects.create(
            title="Создание департамента",
            text="Необходимо добавить информацию по новому департаменту: ",
            author=self.developer
        )
        self.support_task = Task.objects.create(
            title="Назначение менеджера",
            text="В департаменте 'Отдел технической поддержки' назначен новый менеджер. Обновите информацию ",
            author=self.support,
        )
        self.access_develop_token = AuthService.generate_tokens(self.developer)["access"]
        self.access_second_develop_token = AuthService.generate_tokens(self.second_developer)["access"]
        self.access_support_token = AuthService.generate_tokens(self.support)["access"]
        self.access_second_support_token = AuthService.generate_tokens(self.second_support)["access"]
        self.access_security_token = AuthService.generate_tokens(self.security)["access"]
        self.access_hr_token = AuthService.generate_tokens(self.hr)["access"]


class TaskViewSetTests(TaskViewSetBaseSetUp):
    def test_create_task_by_employee(self):
        self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {self.access_develop_token}")
        url = reverse("tasks-list")
        data = {
            "title": "Test",
            "text": "Test",
            "author": self.developer.id
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_task_text_by_author(self):
        self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {self.access_develop_token}")
        url = reverse('tasks-detail', args=[self.developer_task.id])
        data = {
            "text": "Test2"
        }
        response = self.client.patch(url, data, format="json")
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["text"], "Test2")

    def test_update_task_text_not_by_author(self):
        self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {self.access_support_token}")
        url = reverse('tasks-detail', args=[self.developer_task.id])
        data = {
            "text": "Test2"
        }
        response = self.client.patch(url, data, format="json")
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_task_not_by_member(self):
        self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {self.access_develop_token}")
        url = reverse('tasks-detail', args=[self.support_task.id])
        data = {
            "text": "Test2"
        }
        response = self.client.patch(url, data, format="json")
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_task_by_author(self):
        self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {self.access_develop_token}")
        url = reverse('tasks-detail', args=[self.developer_task.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
    def test_delete_task_by_member(self):
        self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {self.access_support_token}")
        url = reverse('tasks-detail', args=[self.developer_task.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_task_not_by_member(self):
        self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {self.access_develop_token}")
        url = reverse('tasks-detail', args=[self.support_task.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_queryset_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {self.access_support_token}")
        url = reverse("tasks-list")
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), Task.objects.count())

    def test_get_queryset_by_other_employees(self):
        self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {self.access_develop_token}")
        url = reverse("tasks-list")
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), Task.objects.filter(Q(author=self.support) | Q(executors=self.developer)).count())

    def test_attach_file_to_task_by_member(self):
        file_content = b'Test file content'
        file = io.BytesIO(file_content)
        file.name = "test_file.txt"
        
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_support_token)
        url = reverse("tasks-upload-files", args=[self.support_task.id])
        data = {
            "files": [file],
        }
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_attach_file_to_task_by_not_a_member(self):
        file_content = b'Test file content'
        file = io.BytesIO(file_content)
        file.name = "test_file.txt"
        
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_develop_token)
        url = reverse("tasks-upload-files", args=[self.support_task.id])
        data = {
            "files": [file],
        }
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# class TaskHistoryViewSetTests(TaskViewSetBaseSetUp):
    def test_get_queryset_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {self.access_support_token}")
        url = reverse("task-history-list")
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), TaskHistory.objects.count())

    def test_get_queryset_by_other_employees(self):
        self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {self.access_develop_token}")
        url = reverse("task-history-list")
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), TaskHistory.objects.filter(Q(task__author=self.developer) | Q(task__executors=self.developer)).count())

    def test_update_note_by_employees(self):
        tokens = [self.access_develop_token, self.access_support_token]
        url = reverse("task-history-detail", args=[1])
        data = {
            "action": "Создание незадачи"
        }
        for token in tokens:
            self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {token}")
            response = self.client.patch(url, data, format="json")
            data = response.json()
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_note_by_employees(self):
        tokens = [self.access_develop_token, self.access_support_token]
        url = reverse("task-history-detail", args=[1])
        for token in tokens:
            self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {token}")
            response = self.client.delete(url, format="json")
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)