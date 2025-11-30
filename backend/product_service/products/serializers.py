from rest_framework import serializers
from django.conf import settings
from django.core.validators import RegexValidator
from .models import Product, ProductImage, Category, Review
from django.db.models import Avg
import logging
import requests

logger = logging.getLogger(__name__)

class HealthCheckSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=10)
    services = serializers.DictField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'category_image', 'category_href']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'image', 'user_id']

class CategoryImageUploadSerializer(serializers.Serializer):
    category_id = serializers.IntegerField()
    image = serializers.ImageField()

    def validate(self, data):
        category_id = data.get('category_id')
        try:
            Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            logger.error(f"Category with ID {category_id} not found")
            raise serializers.ValidationError({"category_id": "Категорія не знайдена"})

        image = data.get('image')
        if image.size > 32 * 1024 * 1024:
            raise serializers.ValidationError({"image": "Розмір зображення не може перевищувати 32 MB"})
        if not image.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            raise serializers.ValidationError({"image": "Дозволені формати: JPG, JPEG, PNG, GIF"})
        return data

class ProductImageUploadSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    image = serializers.ImageField()

    def validate(self, data):
        product_id = data.get('product_id')
        try:
            Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            logger.error(f"Product with ID {product_id} not found")
            raise serializers.ValidationError({"product_id": "Продукт не знайдено"})

        image = data.get('image')
        if image.size > 32 * 1024 * 1024:
            raise serializers.ValidationError({"image": "Розмір зображення не може перевищувати 32MB"})
        if not image.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            raise serializers.ValidationError({"image": "Дозволені формати: .jpg, .jpeg, .png, .gif"})
        return data

class ProductSerializer(serializers.ModelSerializer):
    vendor = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    isAvailable = serializers.SerializerMethodField()
    reviews_count = serializers.IntegerField(read_only=True, source='rating_count')
    productId = serializers.IntegerField(source='id', read_only=True)
    categoryId = serializers.IntegerField(source='category.id', read_only=True)
    rating = serializers.SerializerMethodField()
    discount_tag = serializers.SerializerMethodField()
    is_approved = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'productId', 'vendor', 'categoryId', 'category', 'name', 'description',
            'sale_type', 'price', 'discount_price', 'start_price', 'auction_end_time',
            'stock', 'created_at', 'images', 'product_href', 'isAvailable', 'reviews_count',
            'rating', 'discount_tag', 'is_approved'
        ]
        extra_kwargs = {
            'category': {'write_only': True}
        }

    def get_vendor(self, obj) -> dict:
        request = self.context.get('request')
        auth_header = request.META.get('HTTP_AUTHORIZATION', '') if request else ''

        # Якщо немає токена — повертаємо тільки ID
        if not auth_header:
            return {"id": obj.vendor_id}

        try:
            response = requests.get(
                f"{settings.USER_SERVICE_URL}/api/users/{obj.vendor_id}/",
                headers={'Authorization': auth_header},
                timeout=3
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "id": obj.vendor_id,
                    "username": data.get("username", "unknown"),
                    "email": data.get("email", "")
                }
            else:
                return {"id": obj.vendor_id}
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch vendor {obj.vendor_id}: {e}")
            return {"id": obj.vendor_id}

    def get_isAvailable(self, obj) -> bool:
        return obj.is_available()

    def get_rating(self, obj) -> float:
        average = obj.reviews.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg']
        return round(average, 2) if average is not None else None

    def get_discount_tag(self, obj) -> str:
        if obj.sale_type == 'fixed' and obj.discount_price is not None and obj.price is not None and obj.price > 0:
            discount_percentage = round(((obj.price - obj.discount_price) / obj.price) * 100)
            return f"{discount_percentage}%"
        return None

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['vendor_id'] = request.user.id
        return super().create(validated_data)

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    productId = serializers.IntegerField(source='product.id')
    is_approved = serializers.BooleanField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'productId', 'user', 'rating', 'comment', 'created_at', 'is_approved']
        read_only_fields = ['user', 'created_at', 'is_approved']

    def get_user(self, obj) -> dict:
        request = self.context.get('request')
        auth_header = request.META.get('HTTP_AUTHORIZATION', '') if request else ''

        if not auth_header:
            return {"id": obj.user_id}

        try:
            response = requests.get(
                f"{settings.USER_SERVICE_URL}/api/users/{obj.user_id}/",
                headers={'Authorization': auth_header},
                timeout=3
            )
            if response.status_code == 200:
                data = response.json()
                return {"id": obj.user_id, "username": data.get("username", "unknown")}
            else:
                return {"id": obj.user_id}
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch user {obj.user_id}: {e}")
            return {"id": obj.user_id}

    def validate(self, data):
        product_id = data.get('product', {}).get('id')
        if not Product.objects.filter(id=product_id).exists():
            raise serializers.ValidationError({"productId": "Продукт не знайдений."})
        return data

    def validate_rating(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError("Рейтинг має бути від 0 до 5.")
        return value

    def create(self, validated_data):
        product_id = validated_data.pop('product')['id']
        product = Product.objects.get(id=product_id)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user_id'] = request.user.id
        review = Review.objects.create(
            product=product,
            **validated_data
        )
        return review