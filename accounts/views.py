from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework_simplejwt.views import  TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer,UserRegisterSerializer
# Create your views here.
from .serializers import UserSerializer
from .models import User

class UserViewSet(viewsets.ModelViewSet):
    http_method_names=['get']
    queryset = User.objects.all()
    serializer_class = UserSerializer
class MyTokenObtainPairView(TokenObtainPairView):
  serializer_class = MyTokenObtainPairSerializer

@api_view(['POST'])
def register_user_with_token(request):
  serializer=UserRegisterSerializer(data=request.data)
  serializer.is_valid(raise_exception=True)
  serializer.save()
  return Response(serializer.data,status=status.HTTP_201_CREATED)