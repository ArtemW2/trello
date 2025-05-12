from rest_framework import serializers

from users.models import Employee, Department, ManagerDepartment, EmployeeActionHistory

from users.services.user_service import UserService


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = [
            'login', 'password', 'first_name', 'last_name', 'surname', 'date_of_birth', 'email',
            'department', 'role', 'status', 'hire_date', 'termination_date'
        ]
        read_only_fields = ['role', 'status', 'hire_date', 'termination_date']
        extra_kwargs = {
            'password': {'write_only': True}  
        }

    def validate(self, data):
        data = UserService.validate_data(data, self.context['request'].user)

        return super().validate(data)

    def create(self, validated_data):
        validated_data = UserService.prepare_data_for_create(validated_data)
        employee = Employee.objects.create(**validated_data)
        employee.set_password(validated_data['password'])
        employee.save()

        return employee
    
    def update(self, instance, validated_data):
        instance = UserService.prepare_data_for_update(validated_data, instance)

        for attr, value in validated_data.items():
            if attr != "department" and attr != "password":
                setattr(instance, attr, value)
                
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

        if manager == assistant_manager:
            raise serializers.ValidationError("Руководитель и заместитель руководителя не могут быть одним человеком!")

        if not department:
            raise serializers.ValidationError("Поле department обязательно для заполнения")

        if manager.department_id != department.id or (assistant_manager and assistant_manager.department_id != department.id):
            raise serializers.ValidationError("Руководителем/Заместителем департамента может быть назначен только сотрудник, трудящийся в данном департаменте")
        
        return data
    

class EmployeeActionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeActionHistory
        fields = "__all__"
        read_only_fields = (fields, )