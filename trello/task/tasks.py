from datetime import timedelta

from celery import shared_task

from django.utils import timezone

from task.models import Task

from task.services.monitoring_service import MonitoringService
from task.services.upload_file_service import UploadFileService
from task.services.notification_service import NotificationService


#Отправка сообщения в зависимости от типа информации: создание заявки, изменение приоритета, статуса(все для автора задачи)
@shared_task
def send_task_information_message(task_id = None, recipient_list = None, message_type = None, tasks_info = None, **kwargs):
    NotificationService.send_email_notification(task_id = task_id, recipient_list = recipient_list, message_type = message_type, tasks_info = tasks_info, **kwargs)


#Задача-расписание: Уведомление для всех исполнителей у кого осталось меньше 3 дней по задачам до дедлайна
@shared_task
def check_deadlines():
    deadline_threshold = timezone.now().date() + timedelta(days = 3)
    notification_dict = MonitoringService.get_notifications_group_by_user(deadline_threshold)
    for email, tasks_info in notification_dict.items():
        send_task_information_message.delay(recipient_list = [email], message_type = "deadline_grouped", tasks_info = tasks_info)
    
    
#Загрузка файлов к задачам в облачное хранилище
@shared_task
def upload_task_files_to_google_drive(task, files):
    task = Task.objects.get(id = task)
    UploadFileService.upload_files_to_task(task, files)

@shared_task
def delete_task_files_from_google_drive(file_id):
    UploadFileService.delete_file_from_google_drive(file_id)
