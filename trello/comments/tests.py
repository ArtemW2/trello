from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from users.models import Employee, Department
from task.models import Task
from comments.models import Comment

from users.services.auth_service import AuthService

class CommentsViewSetTests(APITestCase):
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

        self.developer_comment = Comment.objects.create(
            author = self.employee,
            task = self.developer_task,
            text = "Тестовый комментарий",
        )

        self.support_comment = Comment.objects.create(
            author = self.support_employee,
            task = self.developer_task,
            text = "Тестовый комментарий",
        )
       
        support_tokens = AuthService.generate_tokens(self.support_employee)
        develop_tokens = AuthService.generate_tokens(self.employee)
        self.access_develop_token = develop_tokens["access"]
        self.access_support_token = support_tokens["access"]

    def test_create_comment_by_member_of_task(self):
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_develop_token)
        url = reverse("comments-list")
        data = {
            "author": self.employee.id,
            "task": self.developer_task.id,
            "text": "Тестовый комментарий"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_comment_by_not_member_task(self):
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_develop_token)
        url = reverse("comments-list")
        data = {
            "author": self.employee.id,
            "task": self.support_task.id,
            "text": "Тестовый комментарий"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_comment_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_support_token)
        url = reverse("comments-list")
        data = {
            "author": self.support_employee.id,
            "task": self.developer_task.id,
            "text": "Тестовый комментарий"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_own_comment(self):
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_develop_token)
        url = reverse("comments-detail", args=[self.developer_comment.id])
        data = {
            "text": "Изменение тестового комментария",
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_another_comment(self):
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_develop_token)
        url = reverse("comments-detail", args=[self.support_comment.id])
        data = {
            "text": "Изменение тестового комментария",
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_another_comment_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = "Bearer " + self.access_support_token)
        url = reverse("comments-detail", args=[self.developer_comment.id])
        data = {
            "text": "Изменение тестового комментария",
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)