from django.shortcuts import render

# Create your views here.

def home(request):
  return render(request, 'frontend/base.html')

def get_product_list(request):
  return render(request, 'frontend/product_list.html')

def get_product_detail(request,pk):
  context={
    'product_id':pk
  }
  return render(request, 'frontend/product_detail.html',context)

def signup_request(request):
  return render(request, 'frontend/signup.html')