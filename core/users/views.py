from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny

from core.user_middleware import set_current_user

from users.services.auth_service import AuthService
from users.services.user_service import UserService
from users.models import Department, ManagerDepartment, EmployeeActionHistory
from users.services.manager_service import ManagerDepartmentService
from users.permissions import IsManagerOfDepartmentPermission, IsSupportPermission, IsSupportOrOwnerPermission, IsSecurityPermission
from users.serializers import UserSerializer, DepartmentSerializer, ManagerDepartmentSerializer, LoginSerializer, EmployeeActionHistorySerializer

import logging

logger = logging.getLogger(__name__)


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    """
        Добавление и удаление пользователей из системы возможно только для тех.поддержки и руководителя сотрудника
        Обновление данных имеет возможность сам сотрудник и тех.поддержка
        Получить список всех сотрудников только тех.поддержка
    """
    def initial(self, request, *args, **kwargs):
        set_current_user(request.user)
        return super().initial(request, *args, **kwargs)
    
    def get_queryset(self):
        return UserService.get_queryset(self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            logger.info(f"Пользователь {self.request.user} пытается выполнить действие {self.action}")
            return [IsSupportPermission()]
        if self.action in ['update', 'partial_update']:
            logger.info(f"Пользователь {self.request.user} пытается обновить данные сотрудника")
            return [IsSupportOrOwnerPermission()]
        return super().get_permissions()
    

    @action(methods = ['POST'], detail = False, permission_classes = [AllowAny])
    def login(self, request):
        if request.user.is_authenticated:
            logger.warning(f"Пользователь {self.request.user} уже аутентифицирован")
            return Response({'error': 'Пользователь уже аутентифицирован'}, status = status.HTTP_400_BAD_REQUEST)
        
        serializer = LoginSerializer(data = request.data)
        if not serializer.is_valid():
            logger.error("Ошибка в логине или пароле")
            return Response({"error": "Ошибка в логине или пароле"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = AuthService.authenticate_user(
            login = serializer.validated_data["login"],
            password = serializer.validated_data["password"]
        )

        if not user:
            logger.error("Пользователь не найден")
            return Response({"error": "Пользователь не найден"}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = AuthService.generate_tokens(user)
        logger.info(f"Пользователь {user.last_name} {user.first_name} {user.surname} успешно аутентифицирован")
        return Response(tokens, status = status.HTTP_200_OK)

    
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = (IsAuthenticated,)

    """
        Добавление и удаление из системы возможно только для тех.поддержки
        Обновление данных имеет возможность руводитель департамента и тех.поддержка
    """
    def get_permissions(self):
        logger.info(f"Пользователь {self.request.user} пытается выполнить действие {self.action}")
        if self.action in ['create', 'destroy']:
            return [IsSupportPermission()]
        logger.info(f"Пользователь {self.request.user} пытается обновить данные департамента")
        if self.action in ['update', 'partial_update']:
            return [IsSupportPermission()]
        return super().get_permissions()


class ManagerDepartmentViewSet(viewsets.ModelViewSet):
    queryset = ManagerDepartment.objects.all()
    serializer_class = ManagerDepartmentSerializer
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        "Добавление информации о руководителях департамента доступно только для тех.поддержки"
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            logger.info(f"Пользователь {self.request.user} пытается выполнить действие {self.action}")
            return [IsSupportPermission()]
        return super().get_permissions()

    "Получение списка всех сотрудников департамента и списка актуальных задач для них доступно руководителю"
    @action(methods = ['get'], detail = True, url_path = 'executors-tasks', permission_classes = (IsManagerOfDepartmentPermission,))
    def get_info_about_executors(self, request, pk = None):
        try:
            manager_department = self.get_object()
        except Exception as e:
            logger.error(f"Ошибка при поиске менеджера: {e}")
            return Response({'error': "Менеджер не найден"}, status = status.HTTP_404_NOT_FOUND)
        
        executors_data = ManagerDepartmentService.get_info_about_employee_tasks(manager_department.department)
        logger.info(f"Пользователь {request.user} запросил информацию о сотрудниках и задачах департамента {manager_department.department}")
        return Response(executors_data, status = status.HTTP_200_OK)


class EmployeeActionHistoryViewSet(viewsets.ModelViewSet):
    queryset = EmployeeActionHistory.objects.all()
    serializer_class = EmployeeActionHistorySerializer
    permission_classes = (IsSecurityPermission, )
    http_method_names = ['get']