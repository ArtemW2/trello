from rest_framework import serializers

from users.models import Employee, Department, ManagerDepartment


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = [
            'login', 'password', 'first_name', 'last_name', 'surname', 'date_of_birth', 'email',
            'department', 'role', 'status', 'hire_date', 'termination_date'
        ]
        extra_kwargs = {
            'password': {'write_only': True}  
        }

    def create(self, validated_data):
        employee = Employee.objects.create(**validated_data)
        employee.set_password(validated_data['password'])
        employee.save()

        return employee
    
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        return super().update(instance, validated_data)


class LoginSerializer(serializers.Serializer):

    login = serializers.CharField() 
    password = serializers.CharField(write_only=True)


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = '__all__'


class ManagerDepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = ManagerDepartment
        fields = '__all__'

    def validate(self, data):
        manager = data.get("manager")
        assistant_manager = data.get("assistant_manager")
        department = data.get("department")

        if not department:
            raise serializers.ValidationError("Поле department обязательно для заполнения")

        if manager.department_id != department.id or (assistant_manager and assistant_manager.department_id != department.id):
            raise serializers.ValidationError("Руководителем/Заместителем департамента может быть назначен только сотрудник, трудящийся в данном департаменте")
        
        return data