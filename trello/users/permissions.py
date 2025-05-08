from rest_framework.permissions import BasePermission


class IsManagerOfDepartmentPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        return obj.manager == request.user or obj.assistant_manager == request.user
    

class IsSupportOrOwnerPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        return (obj == request.user) or (request.user.department.name == 'Отдел технической поддержки') 
    

class IsSupportPermission(BasePermission):
    def is_support(self, user):
        return user.is_authenticated and user.department.name == 'Отдел технической поддержки' 
    
    def has_permission(self, request, view):
        return self.is_support(request.user)
    
    def has_object_permission(self, request, view, obj):
        return self.is_support(request.user)