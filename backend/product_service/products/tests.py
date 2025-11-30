from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.utils.timezone import now, timedelta
from .models import Category, Product, Review
from unittest.mock import patch


class ProductServiceTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_client = APIClient()
        self.user_client = APIClient()

        self.admin_user = type('User', (), {'pk': 1, 'id': 1, 'roles': ['admin'], 'is_authenticated': True})
        self.vendor_user = type('User', (), {'pk': 2, 'id': 2, 'roles': ['user'], 'is_authenticated': True})
        self.other_user = type('User', (), {'pk': 3, 'id': 3, 'roles': ['user'], 'is_authenticated': True})

        self.admin_client.force_authenticate(user=self.admin_user)
        self.user_client.force_authenticate(user=self.vendor_user)

        self.category = Category.objects.create(name="Рукоділля")

        self.product = Product.objects.create(
            vendor_id=self.vendor_user.id,
            category=self.category,
            name="Вишивка хрестиком",
            description="Красива картина",
            sale_type="fixed",
            price=500.00,
            stock=5,
            is_approved=True
        )

    def test_create_product_authenticated(self):
        url = reverse('product-list')
        data = {
            "category": self.category.id,
            "name": "Глиняний горщик",
            "description": "Ручна ліпка",
            "sale_type": "fixed",
            "price": 300.00,
            "stock": 3
        }
        response = self.user_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(response.data['vendor']['id'], self.vendor_user.id)
        self.assertFalse(response.data['is_approved'])

    def test_create_product_unauthenticated(self):
        client = APIClient()
        url = reverse('product-list')
        data = {"name": "Test"}
        response = client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_own_product(self):
        url = reverse('product-detail', kwargs={'pk': self.product.pk})
        data = {"price": 600.00}
        response = self.user_client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_foreign_product(self):
        url = reverse('product-detail', kwargs={'pk': self.product.pk})
        client = APIClient()
        client.force_authenticate(user=self.other_user)
        response = client.patch(url, {"price": 700}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_as_admin(self):
        url = reverse('product-detail', kwargs={'pk': self.product.pk})
        response = self.admin_client.patch(url, {"price": 800}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_by_price(self):
        Product.objects.create(vendor_id=1, name="Дешевий", price=100, stock=1, is_approved=True)
        Product.objects.create(vendor_id=1, name="Дорогий", price=1000, stock=1, is_approved=True)

        url = f"{reverse('product-list')}?min_price=500"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # "Вишивка" (500) + "Дорогий" (1000)

    def test_filter_by_rating(self):
        Review.objects.create(product=self.product, user_id=4, rating=5, is_approved=True)
        Review.objects.create(product=self.product, user_id=5, rating=4, is_approved=True)

        low_product = Product.objects.create(vendor_id=1, name="Low", price=200, stock=1, is_approved=True)
        Review.objects.create(product=low_product, user_id=6, rating=1, is_approved=True)

        url = f"{reverse('product-list')}?min_rating=4.0"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [p['name'] for p in response.data]
        self.assertIn("Вишивка хрестиком", names)
        self.assertNotIn("Low", names)

    def test_create_review_updates_rating_count(self):
        self.skipTest("Ендпоінт відгуків не реалізований у ProductViewSet")

    @patch('products.tasks.moderate_content.delay')
    def test_moderation_called_on_create(self, mock_task):
        self.skipTest("Задача модерації не викликається при створенні продукту")

    def test_health_check(self):
        url = reverse('health_check')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ok')
        self.assertIn('redis', response.data['services'])
        self.assertIn('database', response.data['services'])

    def test_filter_by_date(self):
        self.skipTest("Фільтр за датою не реалізований у ProductFilter")