from rest_framework import serializers
from .models import Product,ProductImage,Review,Customer
from accounts.serializers import UserSerializer
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


class CustomerSerializer(serializers.ModelSerializer):
  user=UserSerializer(read_only=True)
  class Meta:
    model=Customer
    fields=['id','phone','user','birth_date']

class PrimaryProductReviewSerializer(serializers.ModelSerializer):
  posted_on=serializers.DateTimeField(read_only=True)
  customer=CustomerSerializer()
  
  class Meta:
    model = Review
    fields=['id','title','description','rating','customer','posted_on']   

class ProductReviewSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = Review
    fields=['title','description','rating']   


  def create(self,validated_data):
    title=validated_data['title']
    description=validated_data['description']
    rating=validated_data['rating']
    product_id=self.context['product_id']
    customer=Customer.objects.get(user=self.context['user'])
    product=Product.objects.get(id=product_id)
  
    review=Review.objects.create(
      title=title, description=description,rating=rating, customer=customer, 
      product=product
      )
    print(review)
    review.save()
    return review
    