from rest_framework import serializers
from .models import Menu, MenuItem
from users.models import Order, OrderItem


class MenuItemSerializer(serializers.ModelSerializer):
    image = serializers.URLField(required=False, allow_blank=True)
    
    class Meta:
        model = MenuItem
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'quantity', 'price', 'notes']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    customer = serializers.StringRelatedField()
    restaurant = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = ['id', 'customer', 'restaurant', 'order_items', 'status', 'total_price', 'created_at', 'updated_at', 'delivery_address', 'special_instructions']

class MenuSerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = Menu
        fields = '__all__'