from django.dispatch import receiver
from django.db.models.signals import post_save

from comments.tasks import send_email_notification
from comments.models import Comment

from task.models import TaskHistory

import logging 

logger = logging.getLogger(__name__)

@receiver(post_save, sender = Comment)
def send_notification(sender, instance, created, **kwargs):
    if created and instance.parent_comment:
        send_email_notification.delay(instance.id, instance.parent_comment_id)
        TaskHistory.objects.create(
            task = instance.task,
            employee = instance.author,
            action = f"Добавлен ответ на {instance.parent_comment}",
            new_value = instance.text
        )
        logger.info(f"Было отправлено уведомление о создании ответа на комментарий к задаче №{instance.task} и создана запись в истории действий по задаче")
    
    elif created:
        send_email_notification.delay(instance.id)
        TaskHistory.objects.create(
            task = instance.task,
            employee = instance.author,
            action = "Добавлен комментарий к задаче",
            new_value = instance.text
        )
        logger.info(f"Было отправлено уведомление о создании комментария к задаче №{instance.task} и создана запись в истории действий по задаче")