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
        # self.skipTest("Ендпоінт відгуків не реалізований у ProductViewSet")  # ← remove skip, but if not ready, keep
        url = reverse('review-list')
        data = {"product": {"id": self.product.id}, "rating": 5, "comment": "Great!"}
        response = self.user_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.product.refresh_from_db()
        self.assertEqual(self.product.rating_count, 1)

    @patch('products.tasks.moderate_content.delay')
    def test_moderation_called_on_create(self, mock_task):
        # self.skipTest("Задача модерації не викликається при створенні продукту")  # ← remove skip
        url = reverse('product-list')
        data = {"category": self.category.id, "name": "Test Product", "description": "Test", "sale_type": "fixed", "price": 100, "stock": 1}
        response = self.user_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_task.assert_called_once()

    def test_health_check(self):
        url = reverse('health_check')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ok')
        self.assertIn('redis', response.data['services'])
        self.assertIn('database', response.data['services'])

    def test_filter_by_date(self):
        # self.skipTest("Фільтр за датою не реалізований у ProductFilter")  # ← remove skip if implemented in ProductFilter
        url = f"{reverse('product-list')}?created_after={now().date() - timedelta(days=1)}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ← add these new tests for category
    def test_category_list_anonymous(self):
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)

    def test_category_create_admin(self):
        url = reverse('category-list')
        data = {'name': 'Нова Категорія', 'parent': self.category.id}
        response = self.admin_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])

    def test_category_create_forbidden_regular(self):
        url = reverse('category-list')
        data = {'name': 'Заборонена'}
        response = self.user_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # or 201 if vendor allowed

    def test_category_filter_by_parent(self):
        url = reverse('category-list') + '?parent=null'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)  # assuming self.category is root