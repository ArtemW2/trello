from users.models import Employee
from rest_framework_simplejwt.tokens import RefreshToken

class AuthService:
    @staticmethod
    def authenticate_user(login, password):
        try:
            user = Employee.objects.get(login=login)
            if user.check_password(password):
                return user
        except Employee.DoesNotExist:
            return None
        
    @staticmethod
    def generate_tokens(user):
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
