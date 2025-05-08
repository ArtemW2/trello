from rest_framework import permissions

from task.models import Task

"""
Доступ к просмотру списка задач в зависимости от статуса
Техническая поддержка видит все задачи. Остальные сотрудники только те задачи, в которых участвуют
"""
class TaskPermission(permissions.BasePermission):
    @staticmethod
    def has_task_access(user, task):
       is_author = task.author == user
       is_executor = user in task.executors.all()
       is_support = user.department.name == 'Отдел технической поддержки'

       return is_author or is_executor or is_support
    
    def has_object_permission(self, request, view, obj):
        task = getattr(obj, 'task', obj)
        return self.has_task_access(request.user, task)

"""
Если файл добавляется, то следует проверка является ли автор запроса участником задачи или (тех.поддержкой(надо ли?))
Если кто-то хочет получить список файлов, то он должен быть автором, участником задачи, к которой файл 
Если что-то изменить с файлом, то только тем, кто этот файл разместил
"""
class IsOwnerFilePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create':
            task_id = request.data.get('task')
            try:
                task = Task.objects.get(id = task_id)
            except Task.DoesNotExist:
                return False
            return TaskPermission.has_task_access(request.user, task)
        
        return True
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user == obj.author or request.user in obj.task.executors.all() or request.user == obj.task.author

        return request.user == obj.author