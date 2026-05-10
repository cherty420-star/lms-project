from django.test import TestCase
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from .models import User, Payment
from lms.models import Course


class UserTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'email': 'test@test.com',
            'password': 'test123456',
            'password_confirm': 'test123456',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '+79991234567',
            'city': 'Moscow'
        }

    def test_user_registration(self):
        """Тест регистрации пользователя"""
        url = reverse('user-registration')
        response = self.client.post(url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='test@test.com').exists())

    def test_user_registration_passwords_mismatch(self):
        """Тест регистрации с несовпадающими паролями"""
        url = reverse('user-registration')
        data = self.user_data.copy()
        data['password_confirm'] = 'different'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_duplicate_email(self):
        """Тест регистрации с существующим email"""
        url = reverse('user-registration')
        self.client.post(url, self.user_data, format='json')
        response = self.client.post(url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PaymentTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            password='test123'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Description',
            owner=self.user
        )
        self.client.force_authenticate(user=self.user)

    def test_payment_list(self):
        """Тест получения списка платежей"""
        url = reverse('payment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_payment_filter_by_course(self):
        """Тест фильтрации платежей по курсу"""
        url = reverse('payment-list')
        response = self.client.get(url, {'course': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_payment_filter_by_payment_method(self):
        """Тест фильтрации платежей по способу оплаты"""
        url = reverse('payment-list')
        response = self.client.get(url, {'payment_method': 'cash'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)