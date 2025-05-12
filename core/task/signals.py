# from django.dispatch import receiver
# from django.db.models.signals import post_save, post_delete, m2m_changed

# from core.user_middleware import get_current_user

# from task.models import Task, File
# from task.tasks import send_task_information_message, delete_task_files_from_google_drive

# from task.services.upload_file_service import UploadFileService
# from task.services.task_action_service import TaskHistoryService

# from users.models import Employee


# #Уведомления авторам заявок об успешном создании задачи, а также всем участникам задачи об изменении ее статуса или приоритета
# @receiver(post_save, sender = Task)
# def task_notification(sender, instance, created, **kwargs):
#     recipient_list = [instance.author.email]
#     if created:
#         send_task_information_message.delay(task_id = instance.id, recipient_list = recipient_list, message_type = 'creation')
#     else:
#         recipient_list.extend([e.email for e in instance.executors.all() if e.email])
#         if instance.tracker.has_changed('status'):
#             send_task_information_message.delay(task_id = instance.id, recipient_list = recipient_list, message_type = 'status', status = instance.status)
#         if instance.tracker.has_changed('priority'):
#             send_task_information_message.delay(task_id = instance.id, recipient_list = recipient_list, message_type = 'priority', priority = instance.priority)


# #Информация для авторов заявок о назначенных на задачу исполнителях(ФИО)
# @receiver(m2m_changed, sender = Task.executors.through)
# def task_executors_changed(sender, instance, action, pk_set, **kwargs):
#     if action == "post_add":
#         executors = Employee.objects.filter(id__in = pk_set)
#         executors_names = [f"{e.last_name} {e.first_name} {e.surname}" for e in executors]
#         send_task_information_message.delay(task_id = instance.id, recipient_list = [instance.author.email], message_type = 'executor', executors_names = executors_names)


# @receiver(post_save, sender = File)
# def file_for_the_task_notification(sender, instance, created, **kwargs):
#     if created:
#         recipient_list = [e.email for e in instance.task.executors.all() if e.email]
#         send_task_information_message.delay(task_id = instance.task.id, recipient_list = recipient_list, message_type = 'add_file')


# @receiver(post_save, sender = Task)
# def log_task_action(sender, instance, created, **kwargs):
#     if created:
#         TaskHistoryService.creation(instance)
#     else:
#         TaskHistoryService.tracked_fields_change(instance)

    
# @receiver(m2m_changed, sender = Task.executors.through)
# def log_executors_change(sender, instance, action, pk_set, **kwargs):
#     user = get_current_user()
#     if action == "post_add":
#         TaskHistoryService.update_executors_list(instance, pk_set, user)


# @receiver(post_delete, sender = File)
# def delete_file_from_google_drive(sender, instance, **kwargs):
#     file_url = instance.url
#     file_id = UploadFileService.get_file_id_from_url(file_url)
#     delete_task_files_from_google_drive.delay(file_id)

    
