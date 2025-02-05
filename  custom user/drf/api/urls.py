from django.urls import path
from .views import UserRegisterView, UserLoginView, UserLogoutView, ProtectedView, AddPostView,GetPostView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('post/', AddPostView.as_view(), name='post'),
    path('post/<int:id>/', GetPostView.as_view(), name='post_detail'), # Объедининяем логику в одном представлении

]