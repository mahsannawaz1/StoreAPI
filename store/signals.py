from django.db.models.signals import post_save
from accounts.models import User
from .models import Customer
from django.dispatch import receiver

@receiver(post_save,sender=User)
def create_customer(sender,instance,created,**kwargs):
  if created:
    customer=Customer(phone="XXXX",user=instance)
    customer.save()
    

  