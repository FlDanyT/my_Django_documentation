import secrets
from django.db import models
# from django.contrib.auth.models import User # Встроенная модель пользователя Django
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, login, password=None, lastName=None, birthDate=None):
        if not login:
            raise ValueError("Поле 'login' обязательно")
        
        user = self.model(login=login, lastName=lastName, birthDate=birthDate)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password=None):
        user = self.create_user(login, password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    login = models.CharField(max_length=150, unique=True)
    lastName = models.CharField(max_length=150, blank=True, null=True)
    birthDate = models.DateField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.login

    @property
    def is_staff(self):
        return self.is_admin

class UserToken(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='token') # Меняем на CustomUser
    
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