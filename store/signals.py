from django.db.models.signals import post_save
from accounts.models import User
from .models import Customer,Product,ProductImage
from django.dispatch import receiver
from django.conf import settings
import stripe
from django.shortcuts import redirect

stripe.api_key=settings.STRIPE_SECRET_KEY
@receiver(post_save,sender=User)
def create_customer(sender,instance,created,**kwargs):
  if created:
    customer=Customer(phone="XXXX",user=instance)
    customer.save()

@receiver(post_save,sender=Product)
def create_product_image(sender,instance,created,**kwargs):
  if created:
    image=ProductImage(product=instance)
    image.save()
    
