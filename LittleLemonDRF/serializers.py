from rest_framework import serializers
from .models import MenuItem, Order, OrderItem
from decimal import Decimal
from . import models
import bleach
# class MenuItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.MenuItem
#         fields = ['id', 'title', 'price', 'featured']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ['id', 'slug', 'title']
        


class OrderItemserializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderItem
        fields = ['order', 'menuitem', 'quantity', 'unit_price', 'price']

class OrderSerializer(serializers.ModelSerializer):
    orderitems = models.OrderItem.objects.filter()
    class Meta:
        model= models.Order
        fields = ['user', 'delivery_crew', 'status', 'total', 'date']

class DeliveryCrewOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Order
        fields = ['user', 'delivery_crew', 'status', 'total', 'date']
        extra_kwargs = {
            'user':{'read_only': True}, 
            'delivery_crew':{'read_only': True}, 
            'total':{'read_only': True}, 
            'date':{'read_only': True}}

class OrderViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = ['id','user', 'delivery_crew', 'status', 'total', 'date']
        extra_kwargs = {
            'id':{'read_only':True},
            'user':{'read_only': True}, 
            'delivery_crew':{'read_only': True}, 
            'total':{'read_only': True}, 
            'date':{'read_only': True},
            'status':{'read_only':True}
            }



class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cart
        fields = ['user', 'menuitem', 'quantity', 'unit_price', 'price' ]
        extra_kwargs = {
            'unit_price':{'read_only': True}, 
            'price':{'read_only': True},
            'user': {'read_only':True}
            }


class MenuItemSerializer(serializers.ModelSerializer):
    stock = serializers.IntegerField(source = 'inventory')
    price_after_tax = serializers.SerializerMethodField(method_name= 'calculate_tax')
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only = True)
    featured = serializers.BooleanField()
    
    def validate(self, attrs):
        attrs['title'] = bleach.clean(attrs['title'])
        if(attrs['price']<2):
            raise serializers.ValidationError('Price should not be less than 2.0')
        if(attrs['inventory']<0):
            raise serializers.ValidationError('Stock cannot be negative')
        return super().validate(attrs)
    
    class Meta:
        model = models.MenuItem
        fields = ['id', 'title', 'price', 'stock', 'price_after_tax', 'category', "category_id", "featured"]

    def calculate_tax(self, product:models.MenuItem):
        return product.price * Decimal(1.1)