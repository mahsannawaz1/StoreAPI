from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import  TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer,UserRegisterSerializer
# Create your views here.

class MyTokenObtainPairView(TokenObtainPairView):
  serializer_class = MyTokenObtainPairSerializer

@api_view(['POST'])
def register_user_with_token(request):
  serializer=UserRegisterSerializer(data=request.data)
  serializer.is_valid(raise_exception=True)
  serializer.save()
  return Response(serializer.data,status=status.HTTP_201_CREATED)