from django.shortcuts import render,get_object_or_404
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view,permission_classes
from .models import Product,ProductImage
from django.core.exceptions import ObjectDoesNotExist
from .serializers import ProductSerializer,ProductImageSerializer,CreateProductImageSerializer
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
  
