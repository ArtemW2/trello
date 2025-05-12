from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from comments.serializers import CommentSerializer
from comments.permissions import IsMemberOfTask, IsOwnerOfComment
from comments.services.comment_service import CommentService


import logging
logger = logging.getLogger(__name__)


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return CommentService.get_queryset(self.request.user)

    def get_permissions(self):
        "Добавить комментарий может только участник задачи(автор или любой исполнитель), а также тех.поддержка"
        if self.action in ['create']:
            logger.info(f"Пользователь {self.request.user} пытается создать комментарий")
            return [IsMemberOfTask()]
        if self.action in ['update', 'partial_update', 'destroy']:
            logger.info(f"Пользователь {self.request.user} пытается изменить комментарий")
            return [IsOwnerOfComment()]
        return super().get_permissions()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


