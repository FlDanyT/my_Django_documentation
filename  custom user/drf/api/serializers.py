from django.contrib.auth.models import User
from rest_framework import serializers
from .models import CustomUser, UserToken, Post

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
      model = CustomUser # Меняем на CustomUser
      fields = ['login', 'password', 'lastName', 'birthDate'] # Меняем  новые поля

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data) # Меняем на CustomUser
        return user
class UserLoginSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        from django.contrib.auth import authenticate

        user = authenticate(login=data['login'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Неверные учетные данные")

        token, _ = UserToken.objects.get_or_create(user=user)
        token.generate_token()

        return {'token': token.token}

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'image', 'createdAt']
