from rest_framework import serializers

from comments.models import Comment
from comments.services.comment_service import CommentService

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['task', 'author', 'text', 'parent_comment', 'created_at', 'updated_at']
        read_only_fields = ["author", "parent_comment", "created_at", "updated_at"]

    def validate(self, data):
        data =  CommentService.validate_data(data, self.instance, self.context['request'].user)

        return super().validate(data)
