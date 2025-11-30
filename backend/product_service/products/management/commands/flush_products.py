from django.core.management.base import BaseCommand
from products.models import Category, Product, ProductImage, Review

class Command(BaseCommand):
    help = 'Flush all categories, products, images, and reviews'

    def handle(self, *args, **kwargs):
        Review.objects.all().delete()
        ProductImage.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully flushed all product-related data.'))
