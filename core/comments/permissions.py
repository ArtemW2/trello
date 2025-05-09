from rest_framework.permissions import BasePermission

from task.models import Task

"""
Комментарий можно оставлять только к существующей задаче, если пользователь её автор, исполнитель или техническая поддержка
Доступ к конкретному комментарию на просмотр имеет любой участник задачи
"""
class IsMemberOfTask(BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create':
            task_id = request.data.get('task')
            if not task_id:
                return False
            try:
                task = Task.objects.get(id = task_id)
            except Task.DoesNotExist:
                return False
            
            user = request.user

            if user.department.name == "Отдел технической поддержки":
                return True
            if task.author == user:
                return True
            if user in task.executors.all():
                return True
            return False
        return True


    def has_object_permission(self, request, view, obj):
        return (request.user.department.name == 'Отдел технической поддержки' 
                or request.user == obj.task.author 
                or request.user in obj.task.executors.all())

"""
Удалять изменять комментарий только автор комментария может 
"""
class IsOwnerOfComment(BasePermission):
    def has_object_permission(self, request, view, obj):
       return obj.author == request.user