from rest_framework import serializers
from .models import Product,ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
  image = serializers.SerializerMethodField(method_name='product_image')

  class Meta:
    model=ProductImage
    fields=['image']

  def product_image(self,product_image):
   
    return  f'http://127.0.0.1:8000/{product_image.image.url}'

class ProductSerializer(serializers.ModelSerializer):



  images=ProductImageSerializer(many=True,read_only=True)
  class Meta:
    model=Product
    fields=['id', 'title','description','unit_price','inventory','barcode','images']


class CreateProductImageSerializer(serializers.ModelSerializer):
  
  class Meta:
    model=ProductImage
    fields=['id','image']

  def create(self,validated_data):
    image = ProductImage.objects.create(image=validated_data['image'],product_id=self.context['product_id'])
    image.save()
    return image