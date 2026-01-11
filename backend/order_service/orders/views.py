from rest_framework import viewsets, status
from .mixins import UnifiedResponseMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import Cart, Order, OrderItem, Payment, Shipping
from .serializers import CartSerializer, OrderSerializer
from .permissions import HasRolePermission
from .filters import OrderFilter
from .tasks import reserve_stock, send_order_notification, cancel_pending_orders
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework.generics import GenericAPIView
import requests
from django.conf import settings
import logging
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

@extend_schema_view(
    list=extend_schema(operation_id='cart_list', tags=['cart']),
    retrieve=extend_schema(operation_id='cart_retrieve', tags=['cart']),
    create=extend_schema(operation_id='cart_create', tags=['cart']),
    update=extend_schema(operation_id='cart_update', tags=['cart']),
    partial_update=extend_schema(operation_id='cart_partial_update', tags=['cart']),
    destroy=extend_schema(operation_id='cart_destroy', tags=['cart']),
)
class CartViewSet(UnifiedResponseMixin, viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [HasRolePermission]
    allowed_roles = ['user', 'admin']

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Cart.objects.none()
        return Cart.objects.filter(user_id=self.request.user.id)

    def list(self, request):
        carts = Cart.objects.filter(user_id=request.user.id)
        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_id=request.user.id)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        Cart.objects.filter(user_id=request.user.id, product_id=pk).delete()
        return Response(status=204)


@extend_schema_view(
    list=extend_schema(operation_id='order_list', tags=['orders']),
    retrieve=extend_schema(operation_id='order_retrieve', tags=['orders']),
    create=extend_schema(operation_id='order_create', tags=['orders']),
    update=extend_schema(operation_id='order_update', tags=['orders']),
    partial_update=extend_schema(operation_id='order_partial_update', tags=['orders']),
    destroy=extend_schema(operation_id='order_destroy', tags=['orders']),
)
class OrderViewSet(UnifiedResponseMixin, viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [HasRolePermission]
    allowed_roles = ['user', 'admin']
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend]
    throttle_scope = 'orders'

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Order.objects.none()
        user_roles = getattr(self.request.user, 'roles', [])
        if 'admin' in user_roles:
            return super().get_queryset()
        return self.queryset.filter(customer_id=self.request.user.id)

    @extend_schema(
        operation_id='order_create_from_cart',
        description="Create order from cart",
        tags=['orders'],
    )
    @action(detail=False, methods=['post'])
    def create_from_cart(self, request):
        if not request.user.is_authenticated:
            return Response({"errors": "Authentication required"}, status=401)

        with transaction.atomic():
            cart_items = Cart.objects.filter(user_id=request.user.id)
            if not cart_items.exists():
                return Response({"errors": "Кошик порожній"}, status=400)

            total = 0
            order_items_data = []
            products = {}

            for item in cart_items:
                try:
                    resp = requests.get(
                        f"{settings.PRODUCT_SERVICE_URL}/products/{item.product_id}/",
                        headers={'Authorization': request.headers.get('Authorization', '')},
                        timeout=5
                    )
                    resp.raise_for_status()
                    product = resp.json()
                    products[item.product_id] = product
                except Exception as e:
                    logger.error(f"Product {item.product_id} fetch error: {e}")
                    return Response({"errors": f"Продукт {item.product_id} недоступний"}, status=400)

            for item in cart_items:
                product = products[item.product_id]
                if not product.get('is_approved') or product.get('stock', 0) < item.quantity:
                    return Response({"errors": f"Недостатньо товару: {product['name']}"}, status=400)

                price = product.get('discount_price') or product.get('price')
                total += price * item.quantity
                order_items_data.append(OrderItem(
                    product_id=item.product_id,
                    product_name=product['name'],
                    quantity=item.quantity,
                    price=price,
                    discount_price=product.get('discount_price')
                ))

            order = Order.objects.create(
                customer_id=request.user.id,
                total_amount=total,
                status='pending'
            )

            for oi in order_items_data:
                oi.order = order
                oi.save()

            Payment.objects.create(order=order, method='card', amount=total)
            Shipping.objects.create(order=order, method='nova_poshta', address="Kyiv")

            cart_items.delete()

            # Асинхронне резервування
            reserve_stock.delay(order.id)

            send_order_notification.delay(order.id, 'created')
            return Response(OrderSerializer(order).data, status=201)

    @extend_schema(
        operation_id='order_change_status',
        tags=['orders'],
    )
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({"errors": "Invalid status"}, status=400)
        order.status = new_status
        order.save()
        send_order_notification.delay(order.id, new_status)
        return Response({"status": "updated"})


@extend_schema(exclude=True)
class HealthCheckView(APIView):
    def get(self, request):
        return Response({
            'status': 'ok',
            'services': {
                'redis': {'status': 'ok'},
                'database': {'status': 'ok'}
            }
        })