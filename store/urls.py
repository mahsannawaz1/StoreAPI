
from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('api/products/(?P<product_pk>\d+)/images',views.CreateDeleteProductImageAPIView,basename='product-images')
router.register('api/products/(?P<product_pk>\d+)/reviews',views.ReviewViewSet,basename='product-reviews')
router.register('api/products/(?P<product_pk>\d+)/comments',views.CommentViewSet,basename='product-comments')
urlpatterns = [
    path('api/products/',views.ListCreateProductAPIView.as_view()),  
    path('api/products/<int:pk>/',views.RetrieveUpdateDeleteProductAPIView.as_view(),),
    path('',include(router.urls))
] 
