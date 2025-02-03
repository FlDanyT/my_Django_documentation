**Авторизации по токену**

  **1. Установим зависимости**
  ```python
  pip install djangorestframework django-cors-headers
  django-admin startproject drf
  django-admin startapp api
  ```

  **2. drf/settings.py**
  ```python
  INSTALLED_APPS = [
      'api',
      'rest_framework',
      'corsheaders',
  ]

  REST_FRAMEWORK = {
      'DEFAULT_AUTHENTICATION_CLASSES': (
          'api.authentication.BearerAuthentication',
      ),
      'DEFAULT_PERMISSION_CLASSES': (
          'rest_framework.permissions.IsAuthenticated',
      ),
  }
  ```

  **Таблицы для базы данных**

  **3. api/models.py**
  ```python
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
  ```

  **4. Применяем миграции:**
  ```python
  python manage.py makemigrations api
  python manage.py migrate
  ```

  **5. api/serializers.py:**
  ```python
  from django.contrib.auth.models import User
  from rest_framework import serializers
  from .models import UserToken

  class UserRegisterSerializer(serializers.ModelSerializer):
      password = serializers.CharField(write_only=True, min_length=8)

      class Meta:
          model = User
          fields = ['username', 'email', 'password']

      def create(self, validated_data):
          user = User.objects.create_user(**validated_data)
          UserToken.objects.create(user=user)  # Создаем токен для пользователя
          return user

  class UserLoginSerializer(serializers.Serializer):
      username = serializers.CharField()
      password = serializers.CharField(write_only=True)

      def validate(self, data):
          from django.contrib.auth import authenticate

          user = authenticate(username=data['username'], password=data['password'])
          if not user:
              raise serializers.ValidationError("Неверные учетные данные")

          token, _ = UserToken.objects.get_or_create(user=user)
          token.generate_token()

          return {'token': token.token}
  ```

  **Обрабатывают запросы от клиентов и формируют ответы**

  **6. api/views.py:**
  ```python
  from django.contrib.auth.models import User
  from rest_framework import generics, status
  from rest_framework.response import Response
  from rest_framework.permissions import AllowAny
  from .serializers import UserRegisterSerializer, UserLoginSerializer
  from .models import UserToken

  from rest_framework.views import APIView
  from rest_framework.permissions import IsAuthenticate

  class UserRegisterView(generics.CreateAPIView):
      queryset = User.objects.all()
      serializer_class = UserRegisterSerializer
      permission_classes = [AllowAny]

  class UserLoginView(generics.GenericAPIView):
      serializer_class = UserLoginSerializer
      permission_classes = [AllowAny]

      def post(self, request, *args, **kwargs):
          serializer = self.get_serializer(data=request.data)
          serializer.is_valid(raise_exception=True)
          return Response(serializer.validated_data, status=status.HTTP_200_OK)

  class UserLogoutView(generics.GenericAPIView):
      def post(self, request):
          user = request.user
          if hasattr(user, 'token'):
              user.token.delete()  # Удаляем токен
          return Response({"message": "Вы успешно вышли"}, status=status.HTTP_200_OK)

  class ProtectedView(APIView):
      permission_classes = [IsAuthenticated]

      def get(self, request):
          return Response({"message": "Доступ разрешен"}, status=200)
  ```

  **Проверка токена пользователя**

  **7. api/authentication.py**
  ```python
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
  ```

  **8. api/urls.py**
  ```python
  from django.urls import path
  from .views import UserRegisterView, UserLoginView, UserLogoutView, ProtectedView

  urlpatterns = [
      path('register/', UserRegisterView.as_view(), name='register'),
      path('login/', UserLoginView.as_view(), name='login'),
      path('logout/', UserLogoutView.as_view(), name='logout'),
      path('protected/', ProtectedView.as_view(), name='protected'),
  ]
  ```

  **9. drf/urls.py**
  ```python
  from django.urls import path, include

  urlpatterns = [
      path('api/', include('api.urls')),
  ]
  ```


  Проверка:
  1. Регистрация пользователя
  Метод: POST
  URL: http://127.0.0.1:8000/api/register/
  {
      "username": "testuser",
      "email": "test@example.com",
      "password": "securepassword"
  }

  2. Логин (получение токена)
  Метод: POST
  URL: http://127.0.0.1:8000/api/login/
  {
      "username": "testuser",
      "password": "securepassword"
  }

  3. Запрос к защищённому эндпоинту
  Метод: GET
  URL: http://127.0.0.1:8000/api/protected/
  Authorization: Bearer ...

  4. Logout (выход, удаление токена)
  Метод: POST
  URL: http://127.0.0.1:8000/api/logout/
  Authorization: Bearer ...


**Добавление поста**


  **1. api/models.py**
  ```python
  class Post(models.Model):
      title = models.CharField(max_length=255)
      content = models.TextField()
      image = models.TextField()
      # image = models.ImageField(upload_to='posts/images/', blank=True, null=True)
      createdAt = models.DateTimeField(auto_now_add=True)


      def __str__(self):
          return self.title
  ```

  **2. Применяем миграции:**
  ```python
  python manage.py makemigrations api
  python manage.py migrate
  ```

  **3. api/serializers.py**
  ```python
  from .models import UserToken, Post

  class PostSerializer(serializers.ModelSerializer):
      class Meta:
          model = Post
          fields = ['id', 'title', 'content', 'image', 'createdAt']
  ```

  **4. api/views.py**
  ```python
  from .serializers import UserRegisterSerializer, UserLoginSerializer,PostSerializer

  class AddPostView(APIView):
      permission_classes = [IsAuthenticated] # Проверка авторизации по токену

      def post(self, request):
              serializer = PostSerializer(data=request.data) # Получаем данные
              if serializer.is_valid(): # Делаем проверку на валидацию
                  serializer.save()
                  return Response(serializer.data, status=status.HTTP_201_CREATED)
              return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  ```

  **5. api/urls.py**
  ```python
  from .views import UserRegisterView, UserLoginView, UserLogoutView, ProtectedView, AddPostView

  urlpatterns = [
      path('post/', AddPostView.as_view(), name='post'),
  ]
  ```

  Проверка:

  Метод: POST
  URL: http://127.0.0.1:8000/api/post/

  Authorization: Bearer ...

  {
      "title": "title",
      "content": "content",
      "image": "image",
      "createdAt": "createdAt",
  }


**Просмотр поста по id**


  **1. api/views.py**
  ```python
  from .models import UserToken, Post # Импорт бд постов

  class GetPostView(APIView):
      permission_classes = [IsAuthenticated]

      def get(self, request, id):
          records = Post.objects.filter(id=id) # Берем id и запроса
          serializer = PostSerializer(records, many=True)
          return Response(serializer.data)
  ```

  **2. api/urls.py**
  ```python
  from .views import UserRegisterView, UserLoginView, UserLogoutView, ProtectedView, AddPostView,GetPostView

  urlpatterns = [
      path('post/<int:id>/', GetPostView.as_view(), name='post_get'),
  ]
  ```


  Метод: GET

  URL: http://127.0.0.1:8000/api/post/<int:id>/

  Authorization: Bearer ...


  **Изменение поста**


  **Объединяем логику в одном представлении добавляя в GetPostView def put**

  **1. api/views.py** 
  ```python
  from django.shortcuts import get_object_or_404

  class GetPostView(APIView):
      permission_classes = [IsAuthenticated]
          
      def put(self, request, id):
          post = get_object_or_404(Post, id=id)  # Гарантируем, что объект существует
          serializer = PostSerializer(post, data=request.data, partial=True)  # partial=True позволяет частичное обновление
          if serializer.is_valid():
              serializer.save()
              return Response(serializer.data, status=status.HTTP_200_OK)
          return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  ```

  **2. api/urls.py**
  ```python
  urlpatterns = [
      path('post/<int:id>/', GetPostView.as_view(), name='post_detail'), # Объедининяем логику в одном представлении
  ]
  ```

  Метод: PUT

  URL: http://127.0.0.1:8000/api/post/<int:id>/

  Authorization: Bearer ...

  {
    "title": "title",
      "content": "content",
      "image": "image",
      "createdAt": "createdAt",
  }


**Удаление поста**


  **Объединениям логику в одном представлении добавляя в GetPostView def delete**

  **1. api/views.py**

  ```python 
    class GetPostView(APIView):

    def delete(self, request, id):
        post = get_object_or_404(Post, id=id)
        post.delete()
        return Response({"detail": "Пост удалён"}, status=status.HTTP_204_NO_CONTENT)
  ```

  Метод: DELETE

  URL: http://127.0.0.1:8000/api/post/<int:id>/

  Authorization: Bearer ...


**Все возможности api**

  1. Регистрация пользователя
  Метод: POST
  URL: http://127.0.0.1:8000/api/register/
  {
      "username": "testuser",
      "email": "test@example.com",
      "password": "securepassword"
  }

  2. Логин (получение токена)
  Метод: POST
  URL: http://127.0.0.1:8000/api/login/
  {
      "username": "testuser",
      "password": "securepassword"
  }

  3. Запрос к защищённому эндпоинту
  Метод: GET
  URL: http://127.0.0.1:8000/api/protected/
  Authorization: Bearer ...

  4. Logout (выход, удаление токена)
  Метод: POST
  URL: http://127.0.0.1:8000/api/logout/
  Authorization: Bearer ...
  
  5. Добовление поста
  Метод: POST
  URL: http://127.0.0.1:8000/api/post/

  Authorization: Bearer ...

  {
      "title": "title",
      "content": "content",
      "image": "image",
      "createdAt": "createdAt",
  }

  6. Просмотр поста по ID
  Метод: GET
  URL: http://127.0.0.1:8000/api/post/<int:id>/

  Authorization: Bearer ...

  7. Изменения поста
  Метод: PUT
  URL: http://127.0.0.1:8000/api/post/<int:id>/

  Authorization: Bearer ...

  {
    "title": "title",
      "content": "content",
      "image": "image",
      "createdAt": "createdAt",
  }

  8. Удаление поста
  Метод: DELETE
  URL: http://127.0.0.1:8000/api/post/<int:id>/

  Authorization: Bearer ...
