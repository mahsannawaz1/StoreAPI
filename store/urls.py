
from django.urls import path
from . import views
urlpatterns = [
    path('api/products/',views.ListCreateProductAPIView.as_view()),  
    path('api/products/<int:pk>/',views.RetrieveUpdateDeleteProductAPIView.as_view()),
] 
