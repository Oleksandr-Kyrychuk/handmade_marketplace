from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.timezone import now
from django.db import transaction
from .models import Product, Category, Review
from .serializers import ProductSerializer, ProductImageUploadSerializer, ReviewSerializer, HealthCheckSerializer
from .filters import ProductFilter
from rest_framework.permissions import IsAuthenticated
from .permissions import HasRolePermission, ReviewPermission
from django_filters.rest_framework import DjangoFilterBackend
from .tasks import upload_image_to_cloudinary, send_moderation_notification
import logging
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework.generics import GenericAPIView
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

@extend_schema_view(
    list=extend_schema(
        tags=['products'],
        parameters=[
            OpenApiParameter(name='category', type=int, description='ID категорії'),
            OpenApiParameter(name='min_price', type=float, description='Мінімальна ціна'),
            OpenApiParameter(name='max_price', type=float, description='Максимальна ціна'),
            OpenApiParameter(name='sale_type', type=str, description='Тип продажу: fixed або auction'),
            OpenApiParameter(name='is_approved', type=bool, description='Статус схвалення'),
            OpenApiParameter(name='created_after', type={'format': 'date'}, description='Створено після (YYYY-MM-DD)'),
            OpenApiParameter(name='created_before', type={'format': 'date'}, description='Створено до (YYYY-MM-DD)'),
            OpenApiParameter(name='min_rating', type=float, description='Мінімальний середній рейтинг (0.0–5.0)'),
            OpenApiParameter(name='max_rating', type=float, description='Максимальний середній рейтинг (0.0–5.0)'),
        ]
    ),
    retrieve=extend_schema(tags=['products']),
    create=extend_schema(tags=['products']),
    update=extend_schema(tags=['products']),
    partial_update=extend_schema(tags=['products']),
    destroy=extend_schema(tags=['products']),
)
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [HasRolePermission]
    allowed_roles = ['user', 'admin']
    filterset_class = ProductFilter
    filter_backends = [DjangoFilterBackend]
    throttle_scope = 'products'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            return queryset.filter(stock__gt=0, is_approved=True)
        return queryset

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Авторизація обов'язкова")
        serializer.save(vendor_id=self.request.user.id, is_approved=False)

    def perform_update(self, serializer):
        try:
            with transaction.atomic():
                instance = Product.objects.select_for_update().get(id=serializer.instance.id)
                if instance.vendor_id != self.request.user.id and 'admin' not in self.request.user.roles:
                    logger.warning(f"User {self.request.user.id} attempted to update product {instance.id} without permission")
                    return Response(
                        {"success": False, "errors": {"detail": "Ви не маєте дозволу на редагування цього продукту"}},
                        status=status.HTTP_403_FORBIDDEN
                    )
                if instance.stock < 0:
                    logger.error(f"Invalid stock update for product {instance.id} by user {self.request.user.id}")
                    return Response(
                        {"success": False, "errors": {"stock": ["Запас не може бути від’ємним"]}},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                serializer.save()
                logger.info(f"Product {instance.id} updated by user {self.request.user.id}")
        except Product.DoesNotExist:
            logger.error(f"Product {serializer.instance.id} not found for user {self.request.user.id}")
            return Response(
                {"success": False, "errors": {"detail": "Продукт не знайдено"}},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating product for user {self.request.user.id}: {str(e)}")
            return Response(
                {"success": False, "errors": {"detail": str(e)}},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(tags=['products'])
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_image(self, request, pk=None):
        product = self.get_object()
        if product.vendor_id != request.user.id and 'admin' not in self.request.user.roles:
            logger.warning(f"User {request.user.id} attempted to upload image for product {product.id} without permission")
            return Response(
                {"success": False, "errors": {"detail": "Ви не маєте дозволу на завантаження зображень для цього продукту"}},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = ProductImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            try:
                product_id = serializer.validated_data['product_id']
                image = serializer.validated_data['image']
                upload_image_to_cloudinary.delay(
                    model_type='product',
                    instance_id=product_id,
                    user_id=request.user.id,
                    image_data=image.read(),
                    image_name=image.name
                )
                logger.info(f"Image upload task queued for product {product_id} by user {request.user.id}")
                return Response(
                    {"success": True, "data": {"message": "Завантаження зображення розпочато, URL буде збережено асинхронно"}},
                    status=status.HTTP_202_ACCEPTED
                )
            except Exception as e:
                logger.error(f"Error queuing image upload for user {request.user.id}: {str(e)}")
                return Response(
                    {"success": False, "errors": {"detail": str(e)}},
                    status=status.HTTP_400_BAD_REQUEST
                )
        logger.error(f"Invalid product image upload data for user {request.user.id}: {serializer.errors}")
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(tags=['products'])
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def reviews(self, request, pk=None):
        product = self.get_object()
        reviews = product.reviews.filter(is_approved=True)  # Тільки схвалені
        serializer = ReviewSerializer(reviews, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(tags=['products'])
    @action(detail=True, methods=['patch'], url_path='reserve')
    def reserve(self, request, pk=None):
        product = self.get_object()
        quantity = int(request.data.get('quantity', 0))
        order_id = request.data.get('order_id')

        if quantity <= 0 or not order_id:
            return Response({"error": "quantity and order_id required"}, status=400)

        if product.stock < quantity:
            return Response({"error": "Not enough stock"}, status=400)

        expires_at = timezone.now() + timedelta(hours=24)

        with transaction.atomic():
            Reservation.objects.create(
                product=product,
                order_id=order_id,
                quantity=quantity,
                expires_at=expires_at
            )
            product.stock -= quantity
            product.save(update_fields=['stock'])

        return Response({"success": True, "reserved": quantity})

    @extend_schema(tags=['products'])
    @action(detail=True, methods=['post'], url_path='release')
    def release(self, request, pk=None):
        product = self.get_object()
        order_id = request.data.get('order_id')
        if not order_id:
            return Response({"error": "order_id required"}, status=400)

        with transaction.atomic():
            reservations = product.reservations.filter(order_id=order_id)
            total = sum(r.quantity for r in reservations)
            reservations.delete()
            product.stock += total
            product.save(update_fields=['stock'])

        return Response({"success": True, "released": total})

@extend_schema_view(
    list=extend_schema(
        tags=['moderation'],
        parameters=[
            OpenApiParameter(name='type', description='Type of content to moderate (product/review)', required=True, type=str),
            OpenApiParameter(name='is_approved', description='Filter by approval status', required=False, type=bool),
        ],
        responses={200: ProductSerializer(many=True)},
        description="Retrieve content pending moderation (products or reviews)"
    ),
    create=extend_schema(
        tags=['moderation'],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'type': {'type': 'string', 'enum': ['product', 'review']},
                    'id': {'type': 'integer'},
                    'is_approved': {'type': 'boolean'},
                },
                'required': ['type', 'id', 'is_approved']
            }
        },
        responses={
            200: {'description': 'Content approved or rejected'},
            400: {'description': 'Invalid request'},
            404: {'description': 'Content not found'},
        },
        description="Approve or reject content (product or review)"
    ),
)
class ModerationViewSet(viewsets.ViewSet):
    permission_classes = [HasRolePermission]
    allowed_roles = ['admin']
    throttle_scope = 'moderation'

    def list(self, request):
        content_type = request.query_params.get('type')
        is_approved = request.query_params.get('is_approved', None)

        if content_type not in ['product', 'review']:
            logger.error(f"Invalid content type {content_type} for moderation")
            return Response(
                {"success": False, "errors": {"type": "Тип контенту має бути 'product' або 'review'"}},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if content_type == 'product':
                queryset = Product.objects.all()
                if is_approved is not None:
                    queryset = queryset.filter(is_approved=is_approved.lower() == 'true')
                serializer = ProductSerializer(queryset, many=True)
            else:
                queryset = Review.objects.all()
                if is_approved is not None:
                    queryset = queryset.filter(is_approved=is_approved.lower() == 'true')
                serializer = ReviewSerializer(queryset, many=True)

            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error listing moderation content for type {content_type}: {str(e)}")
            return Response(
                {"success": False, "errors": {"detail": str(e)}},
                status=status.HTTP_400_BAD_REQUEST
            )

    def create(self, request):
        content_type = request.data.get('type')
        content_id = request.data.get('id')
        is_approved = request.data.get('is_approved')

        if content_type not in ['product', 'review']:
            logger.error(f"Invalid content type {content_type} for moderation")
            return Response(
                {"success": False, "errors": {"type": "Тип контенту має бути 'product' або 'review'"}},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(content_id, int):
            logger.error(f"Invalid content ID {content_id} for moderation")
            return Response(
                {"success": False, "errors": {"id": "ID контенту має бути цілим числом"}},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(is_approved, bool):
            logger.error(f"Invalid is_approved value {is_approved} for moderation")
            return Response(
                {"success": False, "errors": {"is_approved": "is_approved має бути булевим значенням"}},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if content_type == 'product':
                obj = Product.objects.get(id=content_id)
                recipient_email = self._get_user_email(obj.vendor_id, request)
            else:
                obj = Review.objects.get(id=content_id)
                recipient_email = self._get_user_email(obj.user_id, request)

            obj.is_approved = is_approved
            obj.save()

            logger.info(f"{content_type.capitalize()} {content_id} {'approved' if is_approved else 'rejected'} by user {request.user.id}")

            send_moderation_notification.delay(content_type, content_id, is_approved, recipient_email)

            return Response(
                {"success": True, "message": f"{content_type.capitalize()} {'схвалено' if is_approved else 'відхилено'}"},
                status=status.HTTP_200_OK
            )

        except (Product.DoesNotExist, Review.DoesNotExist):
            logger.error(f"{content_type.capitalize()} with ID {content_id} not found")
            return Response(
                {"success": False, "errors": {"detail": f"{content_type.capitalize()} не знайдено"}},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error moderating {content_type} {content_id}: {str(e)}")
            return Response(
                {"success": False, "errors": {"detail": str(e)}},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _get_user_email(self, user_id, request):
        try:
            response = requests.get(
                f"{settings.USER_SERVICE_URL}/api/users/{user_id}/",
                headers={'Authorization': request.headers.get('Authorization', '')},
                timeout=5
            )
            response.raise_for_status()
            return response.json().get('email', '')
        except requests.RequestException as e:
            logger.error(f"Error fetching email for user {user_id}: {str(e)}")
            return ''

@extend_schema(
    tags=['health'],
    request=None,
    responses={200: HealthCheckSerializer},
    summary="Health check for Product Service",
    description="Checks Redis and database availability."
)
class HealthCheckView(GenericAPIView):
    serializer_class = HealthCheckSerializer

    def get(self, request):
        return Response({
            'status': 'ok',
            'services': {
                'redis': {'status': 'ok'},
                'database': {'status': 'ok'}
            }
        })

@extend_schema_view(
    list=extend_schema(tags=['reviews']),
    retrieve=extend_schema(tags=['reviews']),
    create=extend_schema(tags=['reviews']),
    update=extend_schema(tags=['reviews']),
    partial_update=extend_schema(tags=['reviews']),
    destroy=extend_schema(tags=['reviews']),
)
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [ReviewPermission]
    allowed_roles = ['user', 'admin']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'rating', 'is_approved', 'created_at'] #фільтри по продукту, рейтингу тощо

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            # Тільки схвалені відгуки для звичайних користувачів
            if 'admin' not in self.request.user.roles:
                queryset = queryset.filter(is_approved=True)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.id, is_approved=False)
        # Асинхронна модерація (REV-08)
        from .tasks import moderate_content
        moderate_content.delay('review', serializer.instance.id, serializer.instance.comment)

    def perform_update(self, serializer):
        # Логіка для редагування (тільки адміни або власник)
        instance = serializer.instance
        if instance.user_id != self.request.user.id and 'admin' not in self.request.user.roles:
            raise PermissionDenied("Ви не можете редагувати цей відгук")
        serializer.save()