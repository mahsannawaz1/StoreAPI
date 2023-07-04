from django.db import models
from django.core.validators import MinValueValidator
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