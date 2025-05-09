from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, m2m_changed

from task.models import Task, File, TaskHistory
from task.tasks import send_task_information_message, delete_task_files_from_google_drive
from task.utils import get_current_user

from task.services.upload_file_service import UploadFileService

from users.models import Employee


#Уведомления авторам заявок об успешном создании задачи, а также всем участникам задачи об изменении ее статуса или приоритета
@receiver(post_save, sender = Task)
def task_notification(sender, instance, created, **kwargs):
    recipient_list = [instance.author.email]
    if created:
        send_task_information_message.delay(task_id = instance.id, recipient_list = recipient_list, message_type = 'creation')
    else:
        recipient_list.extend([e.email for e in instance.executors.all() if e.email])
        if instance.tracker.has_changed('status'):
            send_task_information_message.delay(task_id = instance.id, recipient_list = recipient_list, message_type = 'status', status = instance.status)
        if instance.tracker.has_changed('priority'):
            send_task_information_message.delay(task_id = instance.id, recipient_list = recipient_list, message_type = 'priority', priority = instance.priority)


#Информация для авторов заявок о назначенных на задачу исполнителях(ФИО)
@receiver(m2m_changed, sender = Task.executors.through)
def task_executors_changed(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        executors = Employee.objects.filter(id__in = pk_set)
        executors_names = [f"{e.last_name} {e.first_name} {e.surname}" for e in executors]
        send_task_information_message.delay(task_id = instance.id, recipient_list = [instance.author.email], message_type = 'executor', executors_names = executors_names)


@receiver(post_save, sender = File)
def file_for_the_task_notification(sender, instance, created, **kwargs):
    if created:
        recipient_list = [e.email for e in instance.task.executors.all() if e.email]
        send_task_information_message.delay(task_id = instance.task.id, recipient_list = recipient_list, message_type = 'add_file')


@receiver(post_save, sender = Task)
def log_task_action(sender, instance, created, **kwargs):
    if created:
        TaskHistory.objects.create(
            task = instance,
            employee = instance.author,
            action = f"Создание задачи",
            new_value = instance.title
        )
    else:
        if instance.tracker.has_changed("status"):
            TaskHistory.objects.create(
                task = instance,
                employee = None,
                action = 'Изменение статуса задачи',
                old_value = instance.tracker.previous("status"),
                new_value = instance.status
            )
        # if instance.tracker.has_changed("priority"):
        #     TaskHistory.objects.create(
        #         task = instance,
        #         employee = None,
        #         action = 'Изменение приоритета задачи',
        #         old_value = instance.tracker.previous("priority"),
        #         new_value = instance.priority
        #     )
    
    
@receiver(m2m_changed, sender = Task.executors.through)
def log_executors_change(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        user = get_current_user()
        added_executors = Employee.objects.filter(pk__in = pk_set)
        for executor in added_executors:
            TaskHistory.objects.create(
                task = instance,
                employee = user,
                action = 'Добавлен исполнитель',
                new_value = f'{executor.last_name} {executor.first_name} {executor.surname}'
            )


@receiver(post_delete, sender = File)
def delete_file_from_google_drive(sender, instance, **kwargs):
    file_url = instance.url
    file_id = UploadFileService.get_file_id_from_url(file_url)
    delete_task_files_from_google_drive.delay(file_id)

    


    