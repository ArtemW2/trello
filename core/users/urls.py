from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import EmployeeViewSet, DepartmentViewSet, ManagerDepartmentViewSet, EmployeeActionHistoryViewSet

router = DefaultRouter()

router.register(r'employee', EmployeeViewSet, basename = 'employee')
router.register(r'department', DepartmentViewSet, basename = 'department')
router.register(r'manager-department', ManagerDepartmentViewSet, basename = 'manager')
router.register(r'employee-action', EmployeeActionHistoryViewSet, basename = 'employee-action')

urlpatterns = [
    path('', include(router.urls)),
]
