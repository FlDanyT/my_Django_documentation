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