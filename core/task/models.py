from django.db import models

from model_utils import FieldTracker

from users.models import Employee, Department


class Task(models.Model):
    STATUS_CHOICES = [
        ('open', 'Открыта'),
        ('in_progress', 'В работе'),
        # ('on_review', 'На проверке'), придумать что-то надо
        # ('closed', 'Завершена'), придумать что-то надо
    ]

    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
        ('manager', 'Задача от руководителя департамента')
    ]

    title = models.CharField(max_length = 255, verbose_name = 'Название')
    text = models.TextField(default = "")
    author = models.ForeignKey(Employee, db_index = True, related_name = 'authored_tasks', on_delete = models.CASCADE, verbose_name = 'Автор задачи')
    executors = models.ManyToManyField(Employee, blank = True, related_name = 'executed_tasks', verbose_name = 'Исполнители')
    deadline = models.DateField(blank = True, null = True, db_index = True, verbose_name = 'Срок выполнения')
    department = models.ForeignKey(Department, on_delete = models.CASCADE, null = True, blank = True, related_name = 'responsible_department', verbose_name = 'Ответственный департамент')
    created_at = models.DateTimeField(auto_now_add = True, db_index = True, verbose_name = 'Дата и время создания')
    updated_at = models.DateTimeField(auto_now = True)
    status = models.CharField(max_length = 100, choices = STATUS_CHOICES, default = 'open', verbose_name = 'Статус задачи')
    priority = models.CharField(max_length = 100, choices = PRIORITY_CHOICES, default = 'medium', verbose_name = 'Приоритет')
    tracker = FieldTracker(fields=['status', 'priority', 'executors'])

    def __str__(self):
        return f"{self.id} - {self.title}"
    

class File(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    author = models.ForeignKey(Employee, on_delete=models.CASCADE)
    url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Файл {self.id} к задаче {self.task.id}"
    

class TaskHistory(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name='ID задачи')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='Работник')
    action = models.CharField(max_length=255, verbose_name='Действие')
    old_value = models.CharField(max_length=255, verbose_name='Старое значение')
    new_value = models.CharField(max_length=255, verbose_name='Новое значение')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Выполнено действие '{self.action}' по задаче №{self.task}"