from rest_framework import serializers
from .models import Cart, Order, OrderItem, Payment, Shipping
from django.conf import settings
import requests
import logging
from drf_spectacular.utils import extend_schema_field

logger = logging.getLogger(__name__)

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['product_id', 'quantity']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product_id', 'product_name', 'quantity', 'price', 'discount_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer = serializers.SerializerMethodField()
    payment = serializers.SerializerMethodField()
    shipping = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'customer', 'items', 'total_amount', 'status', 'created_at', 'updated_at', 'payment', 'shipping']
        read_only_fields = ['total_amount', 'created_at', 'updated_at']

    @extend_schema_field(dict)  # Анотація: повертає dict
    def get_customer(self, obj):
        try:
            resp = requests.get(f"{settings.USER_SERVICE_URL}/api/users/{obj.customer_id}/", timeout=3)
            if resp.status_code == 200:
                return resp.json()
        except: pass
        return {"id": str(obj.customer_id)}

    @extend_schema_field(dict)  # Анотація: повертає dict або None
    def get_payment(self, obj):
        if hasattr(obj, 'payment'):
            return {"method": obj.payment.method, "status": obj.payment.status}
        return None

    @extend_schema_field(dict)  # Анотація: повертає dict або None
    def get_shipping(self, obj):
        if hasattr(obj, 'shipping'):
            return {"method": obj.shipping.method, "tracking": obj.shipping.tracking_number}
        return None