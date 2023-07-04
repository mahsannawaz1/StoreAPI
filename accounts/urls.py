
from django.urls import path
from rest_framework_simplejwt.views import  TokenObtainPairView
from .views import MyTokenObtainPairView,register_user_with_token
urlpatterns = [
      path('api/register/',register_user_with_token,name='register_user'),
      path('api/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
] 
