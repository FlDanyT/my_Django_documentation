**1. settings.py** 
```python
AUTH_USER_MODEL = 'api.CustomUser'
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']
```

**Меняем модел**

**2. models.py**
```python
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
```


**Найдите User.objects.all() и замени на CustomUser.objects.all(), а также не забудь импортировать CustomUser**


**3. views.py**
```python
# from django.contrib.auth.models import User
from .models import CustomUser

class UserRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all() # Меняем на CustomUser
```

**4. serializers.py**
```python
from .models import CustomUser, UserToken, Post

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
      model = CustomUser # Меняем на CustomUser
      fields = ['login', 'password', 'lastName', 'birthDate'] # Меняем  новые поля

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data) # Меняем на CustomUser

class UserLoginSerializer(serializers.Serializer):
    login = serializers.CharField() # Меняем на login
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        from django.contrib.auth import authenticate

        user = authenticate(login=data['login'], password=data['password']) # Меняем на login
```

**6. Команды**

rm -rf api/migrations/*.py
rm db.sqlite3
python manage.py makemigrations api
python manage.py migrate

**Новый запрос регистрации**

Регистрация пользователя 

Метод: POST 

URL: http://127.0.0.1:8000/api/register/ 

{ "login": "user", "password": "242141414", "lastName": "user", "birthDate": "DD-YYYY-MM" }