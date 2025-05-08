from django.db.models import Q

from task.models import File

class FileService:
    @staticmethod
    def get_queryset(user):
        return File.objects.filter(Q(author=user) | Q(task__executors=user) | Q(task__author=user)).distinct()