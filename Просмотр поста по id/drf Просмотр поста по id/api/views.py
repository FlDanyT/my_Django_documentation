from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import UserRegisterSerializer, UserLoginSerializer, PostSerializer
from .models import UserToken, Post
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

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

class AddPostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
            serializer = PostSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetPostView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        records = Post.objects.filter(id=id)
        serializer = PostSerializer(records, many=True)
        return Response(serializer.data)