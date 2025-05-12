from django.db import models


from task.models import Task
from users.models import Employee

import textwrap


ROLE_CHOICES = [
    ('author', 'Автор задачи'),
    ('executor', 'Исполнитель')
]

class Comment(models.Model):
    author = models.ForeignKey(Employee, on_delete = models.CASCADE, verbose_name = 'Автор комментария', related_name='author_comment')
    task = models.ForeignKey(Task, db_index = True, on_delete = models.CASCADE, related_name = 'task_comment')
    created_at = models.DateTimeField(auto_now_add = True, db_index = True)
    updated_at = models.DateTimeField(auto_now = True)
    text = models.TextField(verbose_name = 'Текст комментария')
    parent_comment = models.ForeignKey('self', on_delete = models.SET_NULL, related_name = 'replies', blank = True, null = True)

    def get_author_role_in_task(self):
        if self.author == self.task.author:
            return 'author'
        return 'executor'

    def get_replies_all(self):
        comments = Comment.objects.filter(task=self.task).prefetch_related('replies')
        children_list = {}
        for comment in comments:
            parent_id = comment.parent_comment_id
            children_list.setdefault(parent_id, []).append(comment)

        def gather_replies(parent_id):
            result = []
            for child in children_list.get(parent_id, []):
                result.append(child)
                result.extend(gather_replies(child.id))
            return result
            
        return gather_replies(self.id)

    def __str__(self):
        shortened = textwrap.shorten(self.text, width=50, placeholder="...")
        return f"комментарий №{self.id} к задаче {self.task.id}: {shortened}"
    




