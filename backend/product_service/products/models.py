from django.db import models, transaction
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
from cloudinary.models import CloudinaryField
from django.utils.text import slugify

# Валідатор для назви продукту
name_validator = RegexValidator(
    regex=r'^[A-Za-zА-Яа-я0-9\s\-\']+$',
    message="Назва продукту може містити літери, цифри, пробіли, дефіси та одинарні лапки",
    code='invalid_product_name'
)

# Категорії
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, db_index=True)
    category_image = CloudinaryField('image', blank=True, null=True)
    category_href = models.SlugField(max_length=255, unique=True, blank=True)
    search_vector = SearchVectorField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.category_href:
            self.category_href = slugify(self.name) or f"category={self.id or Category.objects.count() + 1}"
            base_href = self.category_href
            counter = 1
            while Category.objects.filter(category_href=self.category_href).exclude(id=self.id).exists():
                self.category_href = f"{base_href}-{counter}"
                counter += 1

        super().save(*args, **kwargs)
        Category.objects.filter(pk=self.pk).update(
            search_vector=SearchVector('name', weight='A', config='simple')
        )

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        indexes = [
            GinIndex(fields=['search_vector'], name='category_search_idx'),
        ]

# Продукти
class Product(models.Model):
    SALE_TYPE_CHOICES = [
        ('fixed', 'Fixed Price'),
        ('auction', 'Auction')
    ]

    vendor_id = models.IntegerField(db_index=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255, db_index=True, validators=[name_validator])
    description = models.TextField(blank=True)
    sale_type = models.CharField(max_length=10, choices=SALE_TYPE_CHOICES, default='fixed', db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_index=True)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_index=True)
    start_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    auction_end_time = models.DateTimeField(null=True, blank=True, db_index=True)
    stock = models.PositiveIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    product_href = models.SlugField(max_length=255, unique=True, blank=True)
    rating_count = models.PositiveIntegerField(default=0, db_index=True)
    search_vector = SearchVectorField(null=True, blank=True)
    is_approved = models.BooleanField(default=False, db_index=True)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.name.strip():
                raise ValueError("Назва продукту не може бути порожньою")

            if not self.product_href:
                self.product_href = slugify(self.name) or f"product-{self.id or Product.objects.count() + 1}"
                base_href = self.product_href
                counter = 1
                while Product.objects.filter(product_href=self.product_href).exclude(id=self.id).exists():
                    self.product_href = f"{base_href}-{counter}"
                    counter += 1

            if self.sale_type == 'fixed' and self.discount_price is not None:
                if self.price is None:
                    raise ValueError("Для типу продаж fixed ціна обов'язкова якщо вказана знижка")
                if self.discount_price > self.price:
                    raise ValueError("Знижена ціна не може бути більшою за звичайну")

            if self.sale_type == 'auction' and self.discount_price is not None:
                self.discount_price = None

            super().save(*args, **kwargs)
            Product.objects.filter(pk=self.pk).update(
                search_vector=(
                        SearchVector('name', weight='A', config='simple') +
                        SearchVector('description', weight='B', config='simple')
                )
            )

    def is_available(self):
        return self.stock > 0 and self.is_approved

    class Meta:
        indexes = [
            GinIndex(fields=['search_vector'], name='product_search_idx'),
        ]

# Зображення продуктів
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    user_id = models.IntegerField(db_index=True)
    image_url = models.URLField(null=True, blank=True)
    image = CloudinaryField('image', null=True, blank=True)

# Резервування stock
class Reservation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reservations')
    order_id = models.UUIDField(db_index=True)
    quantity = models.PositiveIntegerField()
    reserved_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        unique_together = ('product', 'order_id')
        indexes = [
            models.Index(fields=['expires_at'], name='reservation_expires_idx'),
        ]

    def __str__(self):
        return f"Reservation {self.quantity} of {self.product.name} for order {self.order_id}"



# Відгуки
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user_id = models.IntegerField(db_index=True)
    rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], db_index=True)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_approved = models.BooleanField(default=False, db_index=True)

    def save(self, *args, **kwargs):
        old_approved = self.is_approved if self.pk else False
        super().save(*args, **kwargs)
        if self.is_approved and not old_approved:  # Якщо щойно схвалено
            self.product.rating_count = self.product.reviews.filter(is_approved=True).count()
            self.product.save(update_fields=['rating_count'])

    def delete(self, *args, **kwargs):
        product = self.product
        super().delete(*args, **kwargs)
        product.rating_count = product.reviews.filter(is_approved=True).count()
        product.save(update_fields=['rating_count'])


