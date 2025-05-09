from django.utils import timezone

from task.models import Task, TaskHistory

class MonitoringService:
    @staticmethod
    def get_notifications_group_by_user(deadline_threshold):
        tasks_to_update = []
        notification_dict = {}
        tasks = Task.objects.filter(deadline__lte = deadline_threshold).prefetch_related('executors')
        for task in tasks:
            if task.priority != "high":
                old_priority = task.priority
                task.priority = "high"
                tasks_to_update.append((task, old_priority))
            days_left = (task.deadline - timezone.now().date()).days
            for executor in task.executors.all():
                if executor.email:
                    if executor not in notification_dict:
                        notification_dict[executor.email] = []
                    notification_dict[executor.email].append({
                        "task_id": task.id,
                        "task_title": task.title,
                        "recipient_email": executor.email,
                        "days_left": days_left 
                    })
        Task.objects.bulk_update([tasks for tasks,_ in tasks_to_update], ['priority'])

        task_histories = []
        for task, old_priority in tasks_to_update:
            task_histories.append(TaskHistory(
                task = task,
                employee = None,
                action = "Изменение приоритета",
                old_value = old_priority,
                new_value = task.priority
            ))
        TaskHistory.objects.bulk_create(task_histories)
        return notification_dict
            