from django.core.mail import send_mail
from django.conf import settings

import logging

logger = logging.getLogger(__name__)

class NotificationManagerService:
    """
    Шаблоны отправки писем при назначении нового менеджера департамента 
    C сведениями о работниках и при создании новой учётной записи для сотрудника департамента
    """
    
    MESSAGE_TEMPLATES = {
        "employee_created": {
            "subject": "Учётные данные для сотрудника",
            "message": (
                "По вашему запросу была создана учетная запись для сотрудника {last_name} {first_name} {surname}.\n"
                "Для входа в систему сотруднику выданы логин и пароль. Их необходимо изменить при первой авторизации.\n"
                "Логин: {login}\n"
                "Пароль: {password}"
            ),
            "recipients": ["manager_email", "assistant_manager_email"]
        },
        "manager_is_assigned": {
            "subject": "Данные о работниках департамента",
            "message": (
                "{first_name} {surname}, примите наши поздравления с назначением на новую должность.\n"
                "Чтобы Ваша адаптация на новом месте прошла легко, мы собрали для Вас данные о Ваших сотрудниках и их задачах.\n"
                "Надеемся, эта информация Вам пригодится: {executors_data}"
            ),
            "recipients": ["manager_email"],
        }
    }

    @staticmethod
    def send_notification(message_type, context):
        template = NotificationManagerService.MESSAGE_TEMPLATES.get(message_type)
        if not template:
            raise ValueError("Неизвестный шаблон")
        subject = template.get("subject")
        message_template = template.get("message")
        message = message_template.format(**context)
        recipient_list = []
        for key in template.get("recipients", []):
            email = context.get(key)
            if email:
                recipient_list.append(email)

        if not recipient_list:
            raise ValueError("Не найдено получателей")
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=recipient_list,
                fail_silently=False
            )
        except Exception as e:
            logger.error(f"Произошла ошибка при отправке уведомления для руководителя/заместителя: {e}")