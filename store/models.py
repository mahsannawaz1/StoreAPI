from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
from django.conf import settings
# Create your models here.

class Product(models.Model):
  barcode=models.CharField(max_length=12)
  unit_price=models.DecimalField(max_digits=6,decimal_places=2)
  description=models.TextField()
  title=models.CharField(max_length=255)
  inventory=models.PositiveIntegerField(validators=[MinValueValidator(0)])

 
  

  def __str__(self):
    return f'{self.title}'

class ProductImage(models.Model):
  image=models.ImageField(upload_to='products',default='default.png')
  product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='images')
  def __str__(self):
    return f'{self.product.title} image'

class Customer(models.Model):
  MEMBERSHIP_BRONZE='B'
  MEMBERSHIP_SILVER='S'
  MEMBERSHIP_GOLD='G'
  MEMBERSHIP_CHOICES=[
    (MEMBERSHIP_GOLD,'Gold'),
    (MEMBERSHIP_SILVER,'Silver'),
    (MEMBERSHIP_BRONZE,'Bronze'),
  ]
  phone=models.CharField(max_length=15)
  birth_date=models.DateField(null=True,blank=True)
  user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='customer')
  membership=models.CharField(max_length=1,choices=MEMBERSHIP_CHOICES,default=MEMBERSHIP_BRONZE)

  def __str__(self):
    return f'{self.user.first_name} {self.user.last_name} ({self.user.username})'

class Address(models.Model):
  street = models.TextField()
  city=models.CharField(max_length=20)
  state=models.CharField(max_length=20)
  country=models.CharField(max_length=20)
  customer=models.OneToOneField(Customer,on_delete=models.CASCADE,related_name='address')

  def __str__(self):
    return f"{self.customer.user.username}'s Address"

class Comment(models.Model):
  description=models.TextField()
  customer=models.ForeignKey(Customer, on_delete=models.CASCADE,related_name='comments',null=True,blank=True)
  product=models.ForeignKey(Product, on_delete=models.CASCADE,related_name='comments')
  posted_on=models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"{self.customer.user.username}'s Comment {self.id}"

class Review(models.Model):
  title=models.CharField(max_length=30)
  description=models.TextField()
  rating=models.PositiveSmallIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
  customer=models.ForeignKey(Customer, on_delete=models.CASCADE,related_name='reviews',null=True,blank=True)
  product=models.ForeignKey(Product, on_delete=models.CASCADE,related_name='reviews')
  posted_on=models.DateTimeField(auto_now_add=True)
  def __str__(self):
    return f"{self.customer.user.username}'s Review {self.id}"


class Cart(models.Model):
  customer = models.ForeignKey(Customer,on_delete=models.CASCADE,related_name='cart')
  created_at=models.DateTimeField(auto_now_add=True)
  def __str__(self):
    return f"{self.customer.user.username}'s Cart"

class CartItem(models.Model):
  cart=models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
  product=models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
  quantity=models.PositiveIntegerField(validators=[MinValueValidator(1)])
  def __str__(self):
    return f"Cart#{self.cart.id} item"
  

class Order(models.Model):
  ORDER_PENDING='P'
  ORDER_DELIVERED='D'
  ORDER_CANCELLED='C'
  ORDER_STATUS=[
    (ORDER_PENDING,'Pending'),
    (ORDER_DELIVERED,'Delivered'),
    (ORDER_CANCELLED,'Cancelled')
  ]
  payment_status=models.BooleanField(default=False)
  customer=models.ForeignKey(Customer,on_delete=models.CASCADE ,related_name='orders')
  created_at=models.DateTimeField(auto_now_add=True)
  status=models.CharField(max_length=1,choices=ORDER_STATUS,default=ORDER_PENDING)
  checkout_url=models.URLField(null=True, blank=True)
  
  def __str__(self):
    return f"{self.customer.user.username}'s Order"


class OrderItem(models.Model):
  order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='order_items')
  product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='order_items')
  quantity=models.PositiveIntegerField(validators=[MinValueValidator(0)])
  def __str__(self):
    return f"Order#{self.order.id} item"


class Purchase(models.Model):
  customer=models.ForeignKey(Customer, related_name='purchases',on_delete=models.PROTECT)
  order=models.OneToOneField(Order, related_name='purchase',on_delete=models.PROTECT)
  stripe_checkout_session_id=models.CharField(max_length=300,null=True,blank=True)
  is_completed=models.BooleanField(default=False)
