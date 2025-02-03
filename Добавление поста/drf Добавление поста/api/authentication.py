from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
from .models import UserToken

class BearerAuthentication(BaseAuthentication):
    def authenticate(self, request):
      
        auth_header = request.headers.get('Authorization') # Получаем заголовок Authorization из запроса

        if not auth_header or not auth_header.startswith('Bearer '): # Если заголовок отсутствует или не начинается с 'Bearer ', аутентификация не выполняется
            return None  # Без токена — нет авторизации

        token = auth_header.split(' ')[1] # Извлекаем сам токен, убирая 'Bearer '
        try:
            user_token = UserToken.objects.get(token=token) # Ищем токен в базе данных
        except UserToken.DoesNotExist:
            raise AuthenticationFailed('Неверный токен')

        return (user_token.user, None)