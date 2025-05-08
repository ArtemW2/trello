from rest_framework import serializers

from task.models import Task, File, TaskHistory
from task.services.task_service import TaskService

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'author', 'task', 'url', 'uploaded_at']
        read_only_fields = (fields, )

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user

        return File.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        if 'task' in validated_data:
            raise serializers.ValidationError("Нельзя менять ссылку на задачу")
        
        return super().update(instance, validated_data)
    

class TaskSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True, read_only=True)
    class Meta:
        model = Task
        fields = ["id", "author", "executors", "department", "title", "text", "files", "priority", "status"]
        read_only_fields = ['id', 'author', "status"]
        
    def validate(self, data):
        data =  TaskService.validate_data(data, self.instance, self.context['request'].user)

        return super().validate(data)

    def create(self, validated_data):
        validated_data = TaskService.prepare_create_data(validated_data, self.context['request'].user)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = TaskService.prepare_update_data(instance, validated_data)

        return super().update(instance, validated_data)

    
class TaskHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskHistory
        fields = '__all__'
        read_only_fields = (fields, )