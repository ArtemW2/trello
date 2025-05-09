from django.urls import path, include

from rest_framework.routers import DefaultRouter

from task.views import TaskViewSet, FileViewSet, TaskHistoryViewSet

router = DefaultRouter()

router.register(r"tasks", TaskViewSet, basename = 'tasks')
router.register(r"files", FileViewSet, basename = 'files')
router.register(r"task-history", TaskHistoryViewSet, basename = "task-history")

urlpatterns = [
    path('', include(router.urls)),
]
