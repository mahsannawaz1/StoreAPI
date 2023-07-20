from django.urls import path,include
from . import views

urlpatterns = [
    path('products/',views.get_product_list,name='product-list'),  
    path('products/<str:pk>/',views.get_product_detail,name='product-detail'),  
    path('home/',views.home,name='home'),  
   
] 
