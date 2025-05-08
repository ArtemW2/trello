from django.contrib import admin

# Register your models here.
from users.models import Employee, Department, ManagerDepartment

admin.site.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('login', 'first_name', 'last_name', 'department')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.department.name == 'Отдел технической поддержки':
            return qs
        return qs.filter(department=request.user.department)

    def has_view_permission(self, request, obj=None):
        if request.user.department.name == 'Отдел технической поддержки':
            return True
        return super().has_view_permission(request, obj)
    
admin.site.register(Department)
admin.site.register(ManagerDepartment)