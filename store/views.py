from django.shortcuts import render,get_object_or_404
from django.views.generic import View
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from rest_framework.views import APIView
from django.http import HttpResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework.decorators import api_view,permission_classes
from .models import Product,ProductImage,Review,Comment,Customer,Cart,CartItem,Order,OrderItem,Purchase
from django.core.exceptions import ObjectDoesNotExist
from .serializers import ProductSerializer,ProductImageSerializer,CreateProductImageSerializer,ProductReviewSerializer,PrimaryProductReviewSerializer,ProductCommentSerializer,CartSerializer,CartItemSerializer,PrimaryCartItemSerializer,PrimaryProductCommentSerializer,SecondaryCartItemSerializer,OrderSerializer
import stripe
# Create your views here.
endpoint_secret=settings.STRIPE_WEBHOOK_SECRET_KEY
stripe.api_key=settings.STRIPE_SECRET_KEY


@csrf_exempt
def webhook_view(request,*args,**kwargs):
  
  payload=request.body
  sig_header=request.META['HTTP_STRIPE_SIGNATURE']
  event=None

  try:
    event=stripe.Webhook.construct_event(
      payload,sig_header,endpoint_secret
    )
  except ValueError as e:
    # Invalid Payload
    return Response({'error':'Invalid Payload'},status=status.HTTP_400_BAD_REQUEST)
  except stripe.error.SignatureVerificationError as e:
    # Invalid Signature
    return Response({'error':'Invalid Signature'},status=status.HTTP_400_BAD_REQUEST)

  if event['type'] == 'checkout.session.completed':
    session=event['data']['object']

    email=session['customer_details']['email']
    order_id=session['metadata']['order_id']
    order=Order.objects.get(id=order_id)
    items=OrderItem.objects.filter(order=order)

    msg=""
    total=0

    for item in items:
      total += int(item.product.unit_price * item.quantity)
      msg+=f'''
      Name: {item.product.title}  Qty: {item.quantity} Price: {item.product.unit_price} $
      '''
    
    msg+=f'''
                                   Total: {total} $      
      Best Regards,
      StoreAPI   
          '''
    send_mail(
      subject='Here is Your Order Details',
      message=msg,
      recipient_list=[email],
      from_email="admin@gmail.com"
    )
    
  return HttpResponse(status=status.HTTP_200_OK)


class CheckoutSuccessView(APIView):
  permission_classes=[IsAuthenticated]
  http_method_names=['get']
  def get(self, request,pk, *args, **kwargs):
    order=Order.objects.get(id=pk)
    order.payment_status=True
    order.save()
    purchase=Purchase.objects.get(order=order)
    purchase.is_completed=True
    purchase.save()
    return Response({'success':'Your Order has been created successfully.You will shortly recieve an Email'},status=status.HTTP_202_ACCEPTED)

class CheckoutFailedView(APIView):
  permission_classes=[IsAuthenticated]
  http_method_names=['get']
  def get(self, request,pk, *args, **kwargs):
    return Response({'failure':'Payment Details are not valid'},status=status.HTTP_400_BAD_REQUEST)
  
class ListCreateProductAPIView(APIView):

  http_method_names=['get', 'post']

  def get_permissions(self):
    if self.request.method =='POST':
      return [IsAdminUser()]
    return super().get_permissions()

  def get(self,request):
    products=Product.objects.prefetch_related('images').all()
    serializer=ProductSerializer(products,many=True)
    return Response(serializer.data,status=status.HTTP_200_OK)

  def post(self,request):
    serializer=ProductSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data,status=status.HTTP_201_CREATED)

class RetrieveUpdateDeleteProductAPIView(APIView):

  http_method_names=['get', 'put','delete']

  def get_permissions(self):   
    if self.request.method in ['PUT','DELETE']:
      return [IsAdminUser()]
    return super().get_permissions()

  def get(self,request,pk):
    product=get_object_or_404(Product,id=pk)
    serializer=ProductSerializer(product,many=False)
    return Response(serializer.data,status=status.HTTP_200_OK)

  def put(self,request,pk):
    product=get_object_or_404(Product,id=pk)
    serializer=ProductSerializer(product,data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data,status=status.HTTP_202_ACCEPTED)
  
  def delete(self,request,pk):
    product=get_object_or_404(Product,id=pk)
    product.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
 
class CreateDeleteProductImageAPIView(ModelViewSet):

  http_method_names = ['post','delete']
  permission_classes = [IsAdminUser]

  def get_queryset(self):
    return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])

  def get_serializer_context(self):
    return {'product_id': self.kwargs['product_pk']}

  def get_serializer_class(self):
    if self.request.method == 'POST':
      return CreateProductImageSerializer
    return ProductImageSerializer
  
class ReviewViewSet(ModelViewSet):

  http_method_names = ['get', 'post', 'patch', 'delete']
  permission_classes = [IsAuthenticated]

  def get_queryset(self):
      return Review.objects.filter(product_id=self.kwargs['product_pk'])
  
  def get_serializer_context(self):
    return {'user':self.request.user,'product_id':self.kwargs['product_pk']}

  def get_serializer_class(self):
    if self.request.method in ['POST','PATCH','DELETE']:
      return ProductReviewSerializer
    elif self.request.method =='GET':
      return PrimaryProductReviewSerializer
  
class CommentViewSet(ModelViewSet):

  http_method_names = ['get', 'post', 'patch', 'delete']
  permission_classes = [IsAuthenticated]

  def get_queryset(self):
      return Comment.objects.filter(product_id=self.kwargs['product_pk'])
  
  def get_serializer_context(self):
    return {'user':self.request.user,'product_id':self.kwargs['product_pk']}

  def get_serializer_class(self):
    if self.request.method in ['POST','PATCH','DELETE']:
      return ProductCommentSerializer
    elif self.request.method =='GET':
      return PrimaryProductCommentSerializer
  
class CartViewSet(ModelViewSet):

  
  serializer_class=CartSerializer

  def get_queryset(self):
    customer=Customer.objects.get(user__username__icontains="admin")
    return Cart.objects.prefetch_related('cart_items__product').filter(customer=customer)
 
  def get_serializer_context(self):
    return {'user_id': self.request.user.id}
  


class CartItemViewSet(ModelViewSet):

  http_method_names=['get','post','patch','delete']
  

  def get_queryset(self):
    print('cart_id',self.kwargs['cart_pk'])
    return CartItem.objects.prefetch_related('product').filter(cart_id=self.kwargs['cart_pk'])

  def get_serializer_class(self):
    if self.request.method =='POST':
      return CartItemSerializer
    elif self.request.method =='PATCH':
      return SecondaryCartItemSerializer  
    elif self.request.method in ['GET','DELETE']:
      return PrimaryCartItemSerializer
    
  def get_serializer_context(self):
    return {'cart_id': self.kwargs['cart_pk']}

  
class OrderViewSet(ModelViewSet):

  http_method_names=['get', 'post','patch', 'delete']

  def get_serializer_class(self):
    if self.request.method == 'PATCH':
      return PrimaryOrderSerializer
    else:
      return OrderSerializer

  def get_permissions(self):
    if self.request.method in ['PATCH','DELETE']:
      return [IsAdminUser()]
    elif self.request.method in ['GET','POST']:
      return [IsAuthenticated()]

  def get_queryset(self):
    customer=Customer.objects.get(user=self.request.user)  
    return Order.objects.filter(customer=customer)

  def get_serializer_context(self):
    return {'user_id': self.request.user.id}