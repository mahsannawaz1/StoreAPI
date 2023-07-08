from django.shortcuts import render,get_object_or_404
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework.decorators import api_view,permission_classes
from .models import Product,ProductImage,Review,Comment,Customer,Cart,CartItem,Order,OrderItem
from django.core.exceptions import ObjectDoesNotExist
from .serializers import ProductSerializer,ProductImageSerializer,CreateProductImageSerializer,ProductReviewSerializer,PrimaryProductReviewSerializer,ProductCommentSerializer,CartSerializer,CartItemSerializer,PrimaryCartItemSerializer,PrimaryProductCommentSerializer,SecondaryCartItemSerializer,OrderSerializer
# Create your views here.


class ListCreateProductAPIView(APIView):

  http_method_names=['get', 'post']

  def get_permissions(self):
    if self.request.method =='POST':
      return [IsAdminUser()]
    return super().get_permissions()

  def get(self,request):
    products=Product.objects.prefetch_related('images').all()
    serializer=ProductSerializer(products,many=True)
    return Response(serializer.data,status=status.HTTP_200_OK)

  def post(self,request):
    serializer=ProductSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data,status=status.HTTP_201_CREATED)

class RetrieveUpdateDeleteProductAPIView(APIView):

  http_method_names=['get', 'put','delete']

  def get_permissions(self):   
    if self.request.method in ['PUT','DELETE']:
      return [IsAdminUser()]
    return super().get_permissions()

  def get(self,request,pk):
    product=get_object_or_404(Product,id=pk)
    serializer=ProductSerializer(product,many=False)
    return Response(serializer.data,status=status.HTTP_200_OK)

  def put(self,request,pk):
    product=get_object_or_404(Product,id=pk)
    serializer=ProductSerializer(product,data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data,status=status.HTTP_202_ACCEPTED)
  
  def delete(self,request,pk):
    product=get_object_or_404(Product,id=pk)
    product.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
 
class CreateDeleteProductImageAPIView(ModelViewSet):

  http_method_names = ['post','delete']
  permission_classes = [IsAdminUser]

  def get_queryset(self):
    return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])

  def get_serializer_context(self):
    return {'product_id': self.kwargs['product_pk']}

  def get_serializer_class(self):
    if self.request.method == 'POST':
      return CreateProductImageSerializer
    return ProductImageSerializer
  
class ReviewViewSet(ModelViewSet):

  http_method_names = ['get', 'post', 'patch', 'delete']
  permission_classes = [IsAuthenticated]

  def get_queryset(self):
      return Review.objects.filter(product_id=self.kwargs['product_pk'])
  
  def get_serializer_context(self):
    return {'user':self.request.user,'product_id':self.kwargs['product_pk']}

  def get_serializer_class(self):
    if self.request.method in ['POST','PATCH','DELETE']:
      return ProductReviewSerializer
    elif self.request.method =='GET':
      return PrimaryProductReviewSerializer
  
class CommentViewSet(ModelViewSet):

  http_method_names = ['get', 'post', 'patch', 'delete']
  permission_classes = [IsAuthenticated]

  def get_queryset(self):
      return Comment.objects.filter(product_id=self.kwargs['product_pk'])
  
  def get_serializer_context(self):
    return {'user':self.request.user,'product_id':self.kwargs['product_pk']}

  def get_serializer_class(self):
    if self.request.method in ['POST','PATCH','DELETE']:
      return ProductCommentSerializer
    elif self.request.method =='GET':
      return PrimaryProductCommentSerializer
  
class CartViewSet(ModelViewSet):

  permission_classes = [IsAuthenticated]
  serializer_class=CartSerializer

  def get_queryset(self):
    customer=Customer.objects.get(user_id=self.request.user.id)
    return Cart.objects.prefetch_related('cart_items__product').filter(customer=customer)
 
  def get_serializer_context(self):
    return {'user_id': self.request.user.id}

class CartItemViewSet(ModelViewSet):

  http_method_names=['get','post','patch','delete']
  permission_classes = [IsAuthenticated]

  def get_queryset(self):
    print('cart_id',self.kwargs['cart_pk'])
    return CartItem.objects.prefetch_related('product').filter(cart_id=self.kwargs['cart_pk'])

  def get_serializer_class(self):
    if self.request.method =='POST':
      return CartItemSerializer
    elif self.request.method =='PATCH':
      return SecondaryCartItemSerializer  
    elif self.request.method in ['GET','DELETE']:
      return PrimaryCartItemSerializer
    
  def get_serializer_context(self):
    return {'cart_id': self.kwargs['cart_pk']}

  
class OrderViewSet(ModelViewSet):

  http_method_names=['get', 'post','patch', 'delete']

  def get_serializer_class(self):
    if self.request.method == 'PATCH':
      return PrimaryOrderSerializer
    else:
      return OrderSerializer

  def get_permissions(self):
    if self.request.method in ['PATCH','DELETE']:
      return [IsAdminUser()]
    elif self.request.method in ['GET','POST']:
      return [IsAuthenticated()]

  def get_queryset(self):
    customer=Customer.objects.get(user=self.request.user)  
    return Order.objects.filter(customer=customer)

  def get_serializer_context(self):
    return {'user_id': self.request.user.id}