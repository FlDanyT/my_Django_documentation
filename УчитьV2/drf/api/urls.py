from django.urls import path
from .views import UserRegisterView, UserLoginView, PostView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('post/', PostView.as_view(), name='post_create'),          
    path('post/<int:id>/', PostView.as_view(), name='post_detail'),   
]
