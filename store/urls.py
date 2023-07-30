
from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

router = DefaultRouter()
router.register('api/products/(?P<product_pk>\d+)/images',views.CreateDeleteProductImageAPIView,basename='product-image')
router.register('api/products/(?P<product_pk>\d+)/reviews',views.ReviewViewSet,basename='product-review')
router.register('api/products/(?P<product_pk>\d+)/comments',views.CommentViewSet,basename='product-comment')
router.register('api/carts',views.CartViewSet,basename='cart')
router.register('api/orders',views.OrderViewSet,basename='order')

item_router=routers.NestedDefaultRouter(router,'api/carts',lookup='cart')
item_router.register('items',views.CartItemViewSet,basename='item')

urlpatterns = [
    path('api/products/',views.ListCreateProductAPIView.as_view()),  
    path('api/products/<int:pk>/',views.RetrieveUpdateDeleteProductAPIView.as_view(),),
    path('',include(router.urls)),
    path('',include(item_router.urls)),
    path('api/success/<int:pk>',views.CheckoutSuccessView.as_view(),name='success'),
    path('api/failure/',views.CheckoutFailedView.as_view(),name='failure'),
    path('api/webhook/',views.webhook_view,name='webhook'),
     path('api/addresses/',views.CreateAddressAPIView.as_view()),  
    path('api/addresses/<int:pk>/',views.RetrieveUpdateDeleteAddressAPIView.as_view(),),
] 
