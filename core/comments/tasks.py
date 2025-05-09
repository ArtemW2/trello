from celery import shared_task

from comments.services.notification_service import NotificationCommentService


@shared_task
def send_email_notification(comment_id, parent_comment_id = None):
    NotificationCommentService.send_email_notification(comment_id, parent_comment_id)
        

