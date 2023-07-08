from django.contrib import admin
from .models import Product,ProductImage,Customer,Address,Review,Comment,Cart,CartItem,Order,OrderItem
# Register your models here.
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Customer)
admin.site.register(Address)
admin.site.register(Review)
admin.site.register(Comment)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)