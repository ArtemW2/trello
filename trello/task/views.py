from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from task.models import Task, File, TaskHistory
from task.permissions import TaskPermission, IsOwnerFilePermission
from task.serializers import TaskSerializer, FileSerializer, TaskHistorySerializer
from task.tasks import upload_task_files_to_google_drive

from task.services.task_service import TaskService, TaskHistoryService
from task.services.file_service import FileService
from task.services.upload_file_service import UploadFileService

import logging

from task.utils import set_current_user

logger = logging.getLogger(__name__)

# Create your views here.
class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
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
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = (IsAuthenticated, IsOwnerFilePermission)
    
    def get_queryset(self):
        return FileService.get_queryset(self.request.user)
    

class TaskHistoryViewSet(ModelViewSet):
    queryset = TaskHistory.objects.all()
    serializer_class = TaskHistorySerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']

    def get_queryset(self):
        return TaskHistoryService.get_queryset(self.request.user)