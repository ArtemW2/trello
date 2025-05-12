from django.urls import reverse
from django.db.models import Q

from rest_framework.test import APITestCase
from rest_framework import status


from users.models import Employee, Department
from task.models import Task
from comments.models import Comment

from users.services.auth_service import AuthService


class CommentViewSetBaseSetUp(APITestCase):
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
        self.developer_comment = Comment.objects.create(
            author=self.developer,
            task=self.developer_task,
            text="Тестовый комментарий",
        )

        self.support_comment = Comment.objects.create(
            author=self.support,
            task=self.developer_task,
            text="Тестовый комментарий",
        )
        self.access_develop_token = AuthService.generate_tokens(self.developer)["access"]
        self.access_second_develop_token = AuthService.generate_tokens(self.second_developer)["access"]
        self.access_support_token = AuthService.generate_tokens(self.support)["access"]
        self.access_second_support_token = AuthService.generate_tokens(self.second_support)["access"]
        self.access_security_token = AuthService.generate_tokens(self.security)["access"]
        self.access_hr_token = AuthService.generate_tokens(self.hr)["access"]

class CommentViewSetTests(CommentViewSetBaseSetUp):
    def test_create_comment_by_member_of_task(self):
        self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {self.access_develop_token}")
        url = reverse("comments-list")
        data = {
            "task": self.developer_task.id,
            "text": "Тестовый комментарий"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_comment_by_not_member_of_task(self):
        self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {self.access_develop_token}")
        url = reverse("comments-list")
        data = {
            "task": self.support_task.id,
            "text": "Тестовый комметнарий 2"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_own_comment(self):
        self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {self.access_develop_token}")
        url = reverse("comments-detail", args=[self.developer_comment.id])
        data = {
            "text": "Изменение тестового комментария",
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_another_author_comment(self):
        self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {self.access_support_token}")
        url = reverse("comments-detail", args=[self.developer_comment.id])
        data = {
            "text": "Изменение тестового комментария",
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_queryset_by_support(self):
        self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {self.access_support_token}")
        url = reverse("comments-list")
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), Comment.objects.count())

    def test_get_queryset_by_other_employees(self):
        self.client.credentials(HTTP_AUTHORIZATION = f"Bearer {self.access_develop_token}")
        url = reverse("comments-list")
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), Comment.objects.filter(Q(author=self.developer) | Q(task__author=self.developer) | Q(task__executors=self.developer)).count())