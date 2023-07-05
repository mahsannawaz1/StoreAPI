from django.shortcuts import render,get_object_or_404

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .models import Product
from django.core.exceptions import ObjectDoesNotExist
from .serializers import ProductSerializer
# Create your views here.

@api_view()
def product_list(request):
  products=Product.objects.prefetch_related('images').all()
  serializer=ProductSerializer(products,many=True)
  return Response(serializer.data,status=status.HTTP_200_OK)


@api_view()
def product_detail(request,pk):
  
  product=get_object_or_404(Product,id=pk)
  serializer=ProductSerializer(product,many=False)
  return Response(serializer.data,status=status.HTTP_200_OK)
 