from rest_framework.permissions import BasePermission


class IsManagerOfDepartmentPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        return obj.manager == request.user or obj.assistant_manager == request.user
    

class IsSupportPermission(BasePermission):
    @staticmethod
    def is_support(user):
        return user.is_authenticated and user.department.name == 'Отдел технической поддержки' 
    
    def has_permission(self, request, view):
        return self.is_support(request.user)
    
    def has_object_permission(self, request, view, obj):
        return self.is_support(request.user)


class IsSupportOrOwnerPermission(IsSupportPermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        return (obj == request.user) or super().has_object_permission(request, view, obj)


class IsSecurityPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.department.name == "Отдел безопасности"
    
    def has_object_permission(self, request, view, obj):
        return request.user.department.name == "Отдел безопасности"