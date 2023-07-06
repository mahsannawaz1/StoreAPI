
from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('api/products/(?P<product_pk>\d+)/images',views.CreateDeleteProductImageAPIView,basename='product-image')
urlpatterns = [
    path('api/products/',views.ListCreateProductAPIView.as_view()),  
    path('api/products/<int:pk>/',views.RetrieveUpdateDeleteProductAPIView.as_view(),),
    path('',include(router.urls))
] 
