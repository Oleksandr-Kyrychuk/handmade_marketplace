# users/tests.py
from django.test import TestCase, RequestFactory
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from unittest.mock import patch, Mock
from datetime import timedelta
from django.utils import timezone
import logging

from .serializers import RegisterSerializer, UserProfileSerializer, LoginSerializer
from .models import User
from .tasks import mask_email, send_verification_email, is_throttled
from .views import RegisterView, VerifyEmailView, ResendVerificationCodeView, PasswordResetRequestView, PasswordResetConfirmView, UserProfileView, LogoutView, HealthCheckView
from .permissions import HasRolePermission
from .mixins import UnifiedResponseMixin
from user_service.middleware import APILoggingMiddleware


User = get_user_model()

class UserModelTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(email='test@example.com', username='testuser', surname='testsurname', password='password123')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('password123'))
        self.assertEqual(user.roles, ['user'])
        self.assertFalse(user.is_verified)

    def test_email_validation(self):
        with self.assertRaises(ValidationError):
            User.objects.create_user(email='invalid', username='test', surname='test', password='pass')

    def test_name_validation(self):
        with self.assertRaises(ValidationError):
            User.objects.create_user(email='test@example.com', username='--invalid', surname='test', password='pass')

class SerializersTests(TestCase):
    def test_register_serializer(self):
        data = {'username': 'test', 'surname': 'Test', 'email': 'test@example.com', 'password': 'pass123', 'password_confirm': 'pass123', 'agree_terms': True}
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_verified)

    def test_register_password_mismatch(self):
        data = {'username': 'test', 'surname': 'Test', 'email': 'test@example.com', 'password': 'pass123', 'password_confirm': 'wrong', 'agree_terms': True}
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password_confirm', serializer.errors)

    def test_user_profile_serializer(self):
        user = User.objects.create_user(email='profile@test.com', username='profile', surname='user', password='pass')
        serializer = UserProfileSerializer(instance=user)
        self.assertEqual(serializer.data['email'], 'profile@test.com')

class TasksTests(TestCase):
    def test_mask_email(self):
        self.assertEqual(mask_email('testuser@gmail.com'), 'te***@gmail.com')
        self.assertEqual(mask_email('ab@cd.com'), 'ab***@cd.com')
        self.assertEqual(mask_email('invalid'), '***')

    def test_is_throttled(self):
        cache.set('email_reset_test@example.com', True, 60)
        self.assertTrue(is_throttled('test@example.com', 'reset'))

    @patch('users.tasks.send_mail')
    def test_send_verification_email(self, mock_send_mail):
        user = User.objects.create_user(email='verify@test.com', username='verify', surname='user', password='pass')
        send_verification_email(user.id)
        mock_send_mail.assert_called_once()

class PermissionsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='perm@test.com', username='perm', surname='user', password='pass')
        self.request = RequestFactory().get('/')
        self.request.user = self.user
        self.view = Mock()
        self.view.allowed_roles = ['admin']

    def test_has_permission_no_auth(self):
        self.request.user.is_authenticated = False
        perm = HasRolePermission()
        self.assertFalse(perm.has_permission(self.request, self.view))

    def test_has_permission_with_role(self):
        self.user.roles = ['admin']
        perm = HasRolePermission()
        self.assertTrue(perm.has_permission(self.request, self.view))

class ViewsTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

    @patch('users.views.send_verification_email.delay')
    def test_register_view(self, mock_delay):
        url = reverse('register')
        data = {'username': 'reg', 'surname': 'Test', 'email': 'reg@test.com', 'password': 'pass123', 'password_confirm': 'pass123', 'agree_terms': True}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        mock_delay.assert_called_once()

    def test_verify_email_view(self):
        user = User.objects.create_user(email='verify@test.com', username='verify', surname='user', password='pass')
        user.verification_token_created_at = timezone.now()
        user.save()
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        url = reverse('verify-email', kwargs={'uidb64': uid, 'token': token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_verified)

    @patch('users.views.send_verification_email.delay')
    def test_resend_verification_view(self, mock_delay):
        user = User.objects.create_user(email='resend@test.com', username='resend', surname='user', password='pass')
        url = reverse('resend-verification')
        data = {'email': 'resend@test.com'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        mock_delay.assert_called_once()

    def test_login_view(self):
        User.objects.create_user(email='login@test.com', username='login', surname='user', password='pass123', is_verified=True)
        url = reverse('login')
        data = {'email': 'login@test.com', 'password': 'pass123'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_password_reset_request(self):
        user = User.objects.create_user(email='reset@test.com', username='reset', surname='user', password='pass')
        url = reverse('password-reset')
        data = {'email': 'reset@test.com'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_user_profile_view(self):
        user = User.objects.create_user(email='profile@test.com', username='profile', surname='user', password='pass')
        self.client.force_authenticate(user=user)
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_logout_view(self):
        user = User.objects.create_user(email='logout@test.com', username='logout', surname='user', password='pass')
        self.client.force_authenticate(user=user)
        login_response = self.client.post(reverse('login'), {'email': 'logout@test.com', 'password': 'pass'})
        refresh = login_response.data['refresh']
        url = reverse('logout')
        response = self.client.post(url, {'refresh': refresh})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_health_check_view(self):
        url = reverse('health')
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE])
        self.assertIn('status', response.data)

class MiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = APILoggingMiddleware(get_response=lambda r: Response(status=200))

    @patch('logging.Logger.log')
    def test_logging_middleware(self, mock_log):
        request = self.factory.get('/test')
        self.middleware(request)
        mock_log.assert_called_once()

