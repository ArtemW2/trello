from django.contrib import admin

# Register your models here.
from task.models import Task, File, TaskHistory

admin.site.register(Task)
admin.site.register(File)
admin.site.register(TaskHistory)