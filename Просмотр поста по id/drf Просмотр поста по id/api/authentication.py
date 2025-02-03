from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
from .models import UserToken

class BearerAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return None  # Без токена — нет авторизации

        token = auth_header.split(' ')[1]
        try:
            user_token = UserToken.objects.get(token=token)
        except UserToken.DoesNotExist:
            raise AuthenticationFailed('Неверный токен')

        return (user_token.user, None)