from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import EmployeeViewSet, DepartmentViewSet, ManagerDepartmentViewSet

router = DefaultRouter()

router.register(r'employee', EmployeeViewSet, basename = 'employee')
router.register(r'department', DepartmentViewSet, basename = 'department')
router.register(r'manager-department', ManagerDepartmentViewSet, basename = 'manager')

urlpatterns = [
    path('', include(router.urls)),
]
