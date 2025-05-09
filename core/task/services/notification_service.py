from django.core.mail import send_mail
from django.conf import settings

import logging

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def send_email_notification(task_id = None, recipient_list = None, message_type = None, tasks_info = None, **kwargs):
        if message_type == "deadline_grouped" and tasks_info:
            subject = f"Уведомление о приближающихся дедлайнах по задачам"
            message_info = ["Здравствуйте!\n\nУ вас приближаются сроки выполнения следующих задач:\n"]
            for task in tasks_info:
                info = f"Задача №{task['task_id']} - «{task['task_title']}». Осталось {task['days_left']} дн."
                message_info.append(info)
            message_info.append("\nПожалуйста, обратите внимание и постарайтесь выполнить задачи вовремя.")
            message = "\n".join(message_info)
        else:
            subject = f"Информация по задаче №{task_id}"
            message_templates = {
                'creation': "Ваша задача была создана. В скором времени Вам поступит сообщение с информацией об исполнителе и сроках решения проблемы",
                'status': f"Статус Вашей заявки был изменен на <<{kwargs.get('status')}>>",
                'priority': f"Приоритет Вашей заявки был изменен на <<{kwargs.get('priority')}>>",
                "executor": f"К Вашей задаче были назначены новые исполнители: {kwargs.get('executors_names')}",
                "add_file": f"К задаче были приложены новые файлы"
            }
            message = message_templates.get(message_type, "")
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email= settings.EMAIL_HOST_USER,
                recipient_list=recipient_list,
                fail_silently = False
            )
            logger.info(f"Рассылка уведомлений по состоянию задачи №{task_id} произведена по следующим адресам: {recipient_list}")
        except Exception as e:
            logger.error(f"Произошла ошибка при рассылке уведомлений по состоянию задачи №{task_id}: {e}")
    