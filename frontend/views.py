from django.shortcuts import render,redirect
from django.contrib.auth import authenticate
# Create your views here.

def home(request):
  return render(request, 'frontend/base.html')

def get_product_list(request):
  print(request.user)
  return render(request, 'frontend/product_list.html')

def get_product_detail(request,pk):
  context={
    'product_id':pk
  }
  return render(request, 'frontend/product_detail.html',context)

def signup_request(request):
  return render(request, 'frontend/signup.html')

def signin_request(request):
  print('Signing in') 
  
    
  return render(request, 'frontend/signin.html')