from django.urls import path,include
from . import views

urlpatterns = [
    path('products/',views.get_product_list,name='product-list'),  
    path('products/<str:pk>/',views.get_product_detail,name='product-detail'),  
    path('home/',views.home,name='home'),  
    path('signup/',views.signup_request,name='signup'),  
     path('signin/',views.signin_request,name='signin'), 
     path('profile/',views.user_profile,name='profile'),   
   
] 
