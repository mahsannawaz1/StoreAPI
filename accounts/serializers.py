from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        data['username']=self.user.username
        data['email']=self.user.email
        data['image']=self.user.image.url
        return data
        
class UserRegisterSerializer(serializers.ModelSerializer):

  password=serializers.CharField(max_length=100,write_only=True,style={'input_type': 'password'})
  password2=serializers.CharField(max_length=100,write_only=True,style={'input_type': 'password'})
  token=serializers.SerializerMethodField(method_name='get_token')
  class Meta:
    model=User
    fields=['id','username', 'email', 'first_name', 'last_name', 'password', 'password2','token']

  def get_token(self,user):
    token=RefreshToken.for_user(user)
    return str(token.access_token)

  def validate(self,data):
    if data['password']!=data['password2']:
      raise serializers.ValidationError("Passwords doesn't match")
    else:
      return data

  def create(self,validated_data):

    password=make_password(validated_data['password'])
    username=validated_data.get("username")
    email=validated_data.get("email")
    first_name=validated_data.get("first_name")
    last_name=validated_data.get("last_name")

    user=User(username=username,password=password,email=email,first_name=first_name,last_name=last_name)
    user.save()
    return user

class UserSerializer(serializers.ModelSerializer):
  image=serializers.ImageField(read_only=True)
  class Meta:
    model=User
    fields=['email', 'first_name', 'last_name','username','image','is_superuser','is_authenticated']