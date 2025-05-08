from django.core.mail import send_mail
from django.conf import settings

import logging

logger = logging.getLogger(__name__)

class NotificationCommentService:
    @staticmethod
    def send_email_notification(comment_id, parent_comment_id = None):
        from comments.models import Comment
        try:
            comment = Comment.objects.select_related('author','task__author').prefetch_related('task__executors').get(id = comment_id)
        except Comment.DoesNotExist:
            logger.error(f"Комментарий с ID {comment_id} не найден")
            return
        comment_created = comment.created_at.strftime("%d.%m.%Y в %H:%M")
        recipient_list = set()

        if parent_comment_id:
            parent_comment = Comment.objects.select_related('author').get(id = parent_comment_id)
            message = f"Добавлен ответ на комментарий №{parent_comment.id} от {comment_created}"
            recipient_list.add(parent_comment.author.email)
        else:
            message = f"Пользователь {comment.author.last_name} {comment.author.first_name} {comment.author.surname} оставил комментарий от {comment_created}"
            
        if comment.get_author_role_in_task() == "author":
            for employee in comment.task.executors.all():
                if employee.email:
                    recipient_list.add(employee.email)
        else:
            if comment.task.author.email:
                recipient_list.add(comment.task.author.email)
            for employee in comment.task.executors.exclude(id = comment.author.id):
                    if employee.email:
                        recipient_list.add(employee.email)
        if not recipient_list:
            logger.warning(f"Список получателей уведомления пуст")     
            return
        try:
            send_mail(
                    subject = f"Комментарий к задаче №{comment.task.id} - '{comment.task.title}'",
                    message = message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=list(recipient_list),
                    fail_silently=False
                )
            logger.info(f"Уведомления о создании комментария к задаче {comment.task.id} - '{comment.task.title}' было направлено следующим получателям: {recipient_list}")
        except Exception as e:
            logger.error(f"Произошла ошибка при рассылке уведомлений о создании комментария: {e}")

