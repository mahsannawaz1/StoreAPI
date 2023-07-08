from rest_framework import serializers
from .models import Product,ProductImage,Review,Customer,Comment,Cart,CartItem
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


class ProductReviewSerializer(serializers.ModelSerializer):
  id=serializers.IntegerField(read_only=True)
  class Meta:
    model = Review
    fields=['id','title','description','rating']   


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
    review.save()
    return review

class PrimaryProductReviewSerializer(serializers.ModelSerializer):
  posted_on=serializers.DateTimeField(read_only=True)
  customer=CustomerSerializer()
  
  class Meta:
    model = Review
    fields=['id','title','description','rating','customer','posted_on']   



class ProductCommentSerializer(serializers.ModelSerializer):
  id=serializers.IntegerField(read_only=True)
  class Meta:
    model = Comment
    fields=['id','description']   


  def create(self,validated_data):
    
    description=validated_data['description']
    product_id=self.context['product_id']
    customer=Customer.objects.get(user=self.context['user'])
    product=Product.objects.get(id=product_id)
  
    comment=Comment.objects.create(
       description=description, customer=customer,product=product
      )
    comment.save()
    return comment

class PrimaryProductCommentSerializer(serializers.ModelSerializer):
  posted_on=serializers.DateTimeField(read_only=True)
  customer=CustomerSerializer()
  
  class Meta:
    model = Comment
    fields=['id','description','customer','posted_on']   




class CartItemSerializer(serializers.ModelSerializer):
  product=serializers.IntegerField(write_only=True)
  class Meta:
    model=CartItem
    fields=['id','product','quantity']

  def validate_product(self, product):
    if not Product.objects.filter(id=product).exists():
      raise serializers.ValidationError('Product with the given ID not Found')  
    return product

  def create(self,validated_data):
    
    cart_id=self.context['cart_id']
    product=validated_data['product']
    quantity=validated_data['quantity']
    if CartItem.objects.filter(product_id=product).exists():
      cart_item=CartItem.objects.get(product_id=product)
      cart_item.quantity+=quantity
      cart_item.save()
      return cart_item
    else:
      item=CartItem(cart_id=cart_id,product_id=product,quantity=quantity)
      item.save()
      return item

class PrimaryCartItemSerializer(serializers.ModelSerializer):
  product=ProductSerializer()
  total_price=serializers.SerializerMethodField(method_name='cal_total_price')
  
  class Meta:
    model=CartItem
    fields=['id','product','quantity','total_price']
  def cal_total_price(self,cart_item):
    return cart_item.quantity * cart_item.product.unit_price

class SecondaryCartItemSerializer(serializers.ModelSerializer):
  
  class Meta:
    model=CartItem
    fields=['quantity']


class CartSerializer(serializers.ModelSerializer):
  created_at=serializers.DateTimeField(read_only=True)
  customer=CustomerSerializer(read_only=True)
  cart_items=PrimaryCartItemSerializer(read_only=True,many=True)
  total_price=serializers.SerializerMethodField(method_name='cal_total_price')
  class Meta:
    model=Cart 
    fields=['id', 'created_at','customer','cart_items','total_price']

  def cal_total_price(self,cart):
    cart_items=CartItem.objects.filter(cart=cart).values('product__unit_price','quantity') 
    return sum( [ item.get('product__unit_price')*item.get('quantity') for item in cart_items ] )

  def create(self,validated_data):
    customer=Customer.objects.get(user_id=self.context['user_id'])
    
    cart=Cart(customer=customer)
    cart.save()
    return cart

