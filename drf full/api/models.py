import secrets
from django.db import models
from django.contrib.auth.models import User # Встроенная модель пользователя Django

class UserToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='token')
    token = models.CharField(max_length=64, unique=True, blank=True)

    def generate_token(self):
        self.token = secrets.token_hex(32)  # Генерируем безопасный токен
        self.save()
        return self.token

    def __str__(self):
        return f'Token for {self.user.username}' # Ответ серверу

class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.TextField()
    # image = models.ImageField(upload_to='posts/images/', blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title