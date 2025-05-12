from django.core.exceptions import ValidationError

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from task.tasks import upload_task_files_to_google_drive
from task.permissions import TaskPermission, IsOwnerFilePermission
from task.serializers import TaskSerializer, FileSerializer, TaskHistorySerializer

from task.services.file_service import FileService
from task.services.upload_file_service import UploadFileService
from task.services.task_service import TaskService, TaskHistoryService

import logging

from core.user_middleware import set_current_user

logger = logging.getLogger(__name__)


class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated, TaskPermission)

    def initial(self, request, *args, **kwargs):
        set_current_user(request.user)
        super().initial(request, *args, **kwargs)

    #Проверка роли работника, пытающегося получить доступ к информации по задаче
    def get_queryset(self):
        return TaskService.get_queryset(self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        task_id = response.data['id']
        task_title = response.data['title']
        logger.info(f"Пользователь {self.request.user} создал задачу №{task_id} - '{task_title}'")
        return response
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            TaskService.destroy_permission(self.request.user, instance)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    @action(methods=["POST"], detail=True)
    def upload_files(self, request, pk=None):
        task = self.get_object()
        files = request.FILES.getlist("files")

        redis_keys= UploadFileService.upload_files_to_redis(files)

        if not files:
            logger.info(f"Приложите файлы")
            return Response({"message": "Нет файлов для загрузки к выбранной Вами задаче. Для успешного выполнения запроса приложите файлы"}, status=status.HTTP_400_BAD_REQUEST)
        
        files = upload_task_files_to_google_drive.delay(task.id, redis_keys)

        serializer = FileSerializer(files, many=True)
        return Response({"message": "Файлы поставлены в очередь на загрузку"}, status=status.HTTP_202_ACCEPTED)
    
    
class FileViewSet(ModelViewSet):
    serializer_class = FileSerializer
    permission_classes = (IsAuthenticated, IsOwnerFilePermission)
    
    def get_queryset(self):
        return FileService.get_queryset(self.request.user)
    

class TaskHistoryViewSet(ModelViewSet):
    serializer_class = TaskHistorySerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']

    def get_queryset(self):
        return TaskHistoryService.get_queryset(self.request.user)