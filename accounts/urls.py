
from django.urls import path,include
from rest_framework_simplejwt.views import  TokenObtainPairView
from .views import MyTokenObtainPairView,register_user_with_token
from rest_framework.routers import DefaultRouter
from .views import UserViewSet
router = DefaultRouter()
router.register('api/users', UserViewSet)
urlpatterns = [
      path('api/register/',register_user_with_token,name='register_user'),
      path('api/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
      path('', include(router.urls)),
] 
