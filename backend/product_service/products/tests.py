from django.test import TestCase
from rest_framework.test import APIClient
from .models import Product, Category

class ProductTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=type('User', (), {'id': 1, 'roles': ['user'], 'is_authenticated': True}))
        self.category = Category.objects.create(name='Test Category')

    def test_create_product(self):
        data = {
            'category': self.category.id,
            'name': 'Test Product',
            'description': 'Test Description',
            'sale_type': 'fixed',
            'price': 100.00,
            'stock': 10
        }
        response = self.client.post('/products/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.first().name, 'Test Product')
