from rest_framework import serializers
from .models import Product,ProductImage,Review,Customer,Comment,Cart,CartItem,Order,OrderItem,Address,Purchase
from accounts.serializers import UserSerializer
from django.db import transaction
from django.conf import settings
import stripe
from django.shortcuts import redirect
stripe.api_key=settings.STRIPE_SECRET_KEY

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

  def create(self,validated_data):
    stripe_product=stripe.Product.create(name=validated_data['title'])
    stripe_price=stripe.Price.create(
      product=stripe_product.id,
      unit_amount=int(validated_data['unit_price']*100),
      currency='usd'
    )
    price=validated_data['unit_price'] *100
    product=Product(**validated_data,stripe_product_id=stripe_product.id,stripe_price_id=stripe_price.id,stripe_price=price)
    product.save()
    return product



    
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
    product_id=validated_data['product']
    print(product_id)
    quantity=validated_data['quantity']
    product=Product.objects.get(id=product_id)
    if quantity > product.inventory:
      raise serializers.ValidationError(
        f'''Product with the given ID have only {product.inventory} items left in Stock'''
        )
    else:
      if CartItem.objects.filter(product_id=product_id).exists():
        cart_item=CartItem.objects.get(product_id=product_id)
        cart_item.quantity+=quantity
        cart_item.save()
        print('old')
        return cart_item
      else:
        print('new')
        item=CartItem(cart_id=cart_id,product_id=product_id,quantity=quantity)
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

  def update(self,instance,validated_data,*args,**kwargs):
   
    if validated_data['quantity'] > instance.product.inventory:
      raise serializers.ValidationError(
        f'''Product have only {instance.product.inventory} items left in Stock'''
        )
    else:
      instance.quantity =validated_data['quantity'] 
      instance.save()
      return instance



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
    customer=""
    if self.context['user_id'] is None:
      customer=Customer.objects.get(user__username__icontains="admin")
    else:
      customer=Customer.objects.get(user_id=self.context['user_id'])
    
    cart=Cart(customer=customer)
    cart.save()
    return cart


class PrimaryOrderItemSerializer(serializers.ModelSerializer):
  product=ProductSerializer()
  total_price=serializers.SerializerMethodField(method_name='cal_total_price')
  
  class Meta:
    model=CartItem
    fields=['id','product','quantity','total_price']
  def cal_total_price(self,order_item):
    return order_item.quantity * order_item.product.unit_price

class OrderSerializer(serializers.ModelSerializer):
  cart_id = serializers.IntegerField(write_only=True)
  checkout_url=serializers.URLField(read_only=True)
  class Meta:
    model=Order
    fields=['cart_id','checkout_url']

  def validate_cart_id(self, cart_id):
    if not Cart.objects.filter(id=cart_id).exists():
      
      raise serializers.ValidationError('Cart with the given ID not Found')
    if not CartItem.objects.filter(cart_id=cart_id).exists():
      raise serializers.ValidationError('Cart with the given ID has 0 Items')
    else:  
      return cart_id

  def create(self,validated_data):
    with transaction.atomic():
      customer=Customer.objects.get(user_id=self.context['user_id'])
      if not Address.objects.filter(customer=customer).exists():
        raise serializers.ValidationError('Customer must have an address to create an order')
      else:  
        cart_id=validated_data['cart_id']

        order=Order(customer=customer)
        order.save()
        
        items=CartItem.objects.filter(cart_id=cart_id)
        items=list(items)

        order_items=[
          OrderItem(order=order,product=item.product,quantity=item.quantity) 
          for item in items
          ]
        it=OrderItem.objects.bulk_create(order_items)
        cart=Cart.objects.get(id=cart_id)
        # cart.delete()
        print(items)
        print(order_items)
        line_items=[
         {
          'price_data':{
            'currency':'usd',
            'unit_amount':int(item.product.unit_price)*100,
            'product_data':{
              'name':item.product.title
              }
          },

          'quantity':item.quantity
         } 
         for item in items
        ]

        

        checkout_session=stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='payment',
            line_items=line_items,
            customer_email=customer.user.email,
            metadata={
              'order_id': order.id
            },
            success_url=f'http://127.0.0.1:8000/api/success/{order.id}',
            cancel_url='http://127.0.0.1:8000/api/failure/'

        )
        
        purchase=Purchase(
          order=order,customer=customer,stripe_checkout_session_id=checkout_session.id
          )
        purchase.save()

        order.checkout_url = checkout_session.url
        order.save()

        return order
  
  def cal_total_price(self,order):
    order_items=OrderItem.objects.filter(order=order).values('product__unit_price','quantity') 
    return sum( [ item.get('product__unit_price')*item.get('quantity') for item in order_items ] )
    
    

class PrimaryOrderSerializer(serializers.ModelSerializer):
  
  class Meta:
    model=Order
    fields=['status']

  def validate_status(self,value):
    if value not in ['P','D','C']:
      raise serializers.ValidationError('Invalid status Value Entered')
    else:
      return value

  def update(self,instance,*args,**kwargs):
    status=validated_data.get('status')
    if status =='D':
      order_items=OrderItem.objects.filter(order=instance)
      for item in items:
        product=Product.objects.get(id=item.product.id)
        product.inventory-=item.quantity
        product.save()
    elif status =='C':
      order_items=OrderItem.objects.filter(order=instance)
      for item in items:
        product=Product.objects.get(id=item.product.id)
        product.inventory+=item.quantity
        product.save()

    instance.status=status
    return instance

  