from datetime import timedelta

from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q

from comments.models import Comment
from users.models import DepartmentChoices, ManagerDepartment

class CommentService:
    """
    Пользователь видит все свои комментарии и те, что относятся к причастным к нему задачам
    """
    @staticmethod
    def get_queryset(user):
        if hasattr(user, 'department') and user.department and user.department.name == DepartmentChoices.SUPPORT.value:
            return Comment.objects.all()
        if ManagerDepartment.objects.filter(Q(manager=user) | Q(assistant_manager=user)).exists():
            return Comment.objects.filter(Q(author=user) | Q(task__author=user) | Q(task__executors=user) | Q(task__department=user.department))
        else:
            return Comment.objects.filter(Q(author=user) | Q(task__executors=user) | Q(task__author=user)).distinct()

    """
    Редактировать можно в течение 15 минут
    Ответ можно оставить только на комментарий, причастный к задаче
    """
    @staticmethod
    def validate_data(data, instance, context_user):

        if instance:
            comment_change_time_limit = timezone.now() - instance.created_at

            if comment_change_time_limit > (timedelta(15*60)):
                raise ValidationError("Редактирование невозможно")
            
        parent_comment = data.get('parent_comment')
        task = data.get('task')

        if parent_comment and task:
            if isinstance(parent_comment, int) or isinstance(parent_comment, str):
                try:
                    parent_comment_obj = Comment.objects.get(id=parent_comment)
                except Comment.DoesNotExist:
                    raise ValidationError("Родительский комментарий не найден")
            else:
                parent_comment_obj = parent_comment  

            parent_task_id = parent_comment_obj.task_id
            task_id = task.id if hasattr(task, 'id') else task  

            if parent_task_id != task_id:
                raise ValidationError("Нельзя оставить ответ на комментарий к другой задаче")

        return data