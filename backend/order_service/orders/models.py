from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
import uuid
from django.db.models.functions import Cast
from django.db.models import TextField

class Cart(models.Model):
    user_id = models.UUIDField(db_index=True, default=uuid.uuid4)
    product_id = models.UUIDField(db_index=True, default=uuid.uuid4)  # Changed to UUID for consistency
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user_id', 'product_id')
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        return f"Cart {self.user_id} — {self.product_id} x{self.quantity}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reserved', 'Reserved'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    ]

    customer_id = models.UUIDField(db_index=True, default=uuid.uuid4)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        indexes = [GinIndex(fields=['search_vector'], name='order_search_idx')]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Order.objects.filter(pk=self.pk).update(
            search_vector=SearchVector(Cast('id', TextField()), 'status', config='simple')  # Fixed int cast issue
        )

    def __str__(self):
        return f"Order #{self.id} — {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_id = models.UUIDField(default=uuid.uuid4)
    product_name = models.CharField(max_length=255, default='')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    method = models.CharField(max_length=50, default='card')
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class Shipping(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipping')
    method = models.CharField(max_length=100, default='nova_poshta')
    tracking_number = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(default='')
    city = models.CharField(max_length=100, default='')
    shipped_at = models.DateTimeField(null=True, blank=True)

class EmailLog(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='emails')
    subject = models.CharField(max_length=255, default='')
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='sent')