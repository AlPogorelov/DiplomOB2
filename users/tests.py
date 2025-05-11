from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from .models import Payment, Subscription
from content.models import Content, Category

User = get_user_model()


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(phone='79123456789', password='testpass')
        self.assertEqual(user.phone, '79123456789')

    def test_create_superuser(self):
        admin = User.objects.create_superuser(phone='79000000000', password='adminpass')
        self.assertTrue(admin.is_superuser)


class PaymentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone='79123456789', password='testpass')
        self.category = Category.objects.create(name='Test Category')
        self.content = Content.objects.create(
            title='Test Content',
            category=self.category,
            sub_price=100,
            owner=self.user
        )

    def test_payment_creation(self):
        payment = Payment.objects.create(
            user=self.user,
            content=self.content,
            amount=100,
            session_id='test_session'
        )
        self.assertEqual(payment.status, 'pending')


class SubscriptionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone='+79123456789', password='testpass')
        self.category = Category.objects.create(name='машины')
        self.content = Content.objects.create(
            title='Test Content',
            sub_price=100,
            owner=self.user,
            category=self.category
        )

    def test_unique_subscription(self):
        Subscription.objects.create(user=self.user, content=self.content)
        with self.assertRaises(Exception):
            Subscription.objects.create(user=self.user, content=self.content)


class UserAuthTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            phone='79123456789',
            password='testpass123'  # Пароль будет хеширован
        )


class PaymentViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(phone='79123456789', password='testpass')
        self.category = Category.objects.create(name='Test Category')
        self.content = Content.objects.create(
            title='Test Content',
            sub_price=100,
            owner=self.user,
            category=self.category
        )
        self.client.login(phone='79123456789', password='testpass')

    @patch('stripe.checkout.Session.create')
    def test_create_payment(self, mock_stripe):
        mock_session = MagicMock()
        mock_session.id = 'test_session'
        mock_session.url = 'http://test.url'
        mock_stripe.return_value = mock_session

        response = self.client.get(reverse('users:create_payment', args=[self.content.id]))
        self.assertEqual(response.status_code, 200)

    @patch('stripe.checkout.Session.retrieve')
    def test_payment_success(self, mock_stripe):
        payment = Payment.objects.create(
            user=self.user,
            content=self.content,
            amount=100,
            session_id='test_session',
            status='pending'
        )
        mock_stripe.return_value = MagicMock(payment_status='paid', payment_intent='test_intent')
        response = self.client.get(
            reverse('users:payment_success', args=[self.content.id]),
            {'session_id': 'test_session'}
        )
        self.assertEqual(response.status_code, 302)
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'paid')


class FullPaymentFlowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(phone='79123456789', password='testpass')
        self.category = Category.objects.create(name='машины')
        self.content = Content.objects.create(
            title='Premium Content',
            sub_price=100,
            owner=self.user,
            category=self.category
        )
        self.client.login(phone='79123456789', password='testpass')

    @patch('stripe.checkout.Session.create')
    @patch('stripe.checkout.Session.retrieve')
    def test_full_payment_flow(self, mock_retrieve, mock_create):
        # Настраиваем моки
        mock_session = MagicMock()
        mock_session.id = 'test_session'
        mock_session.url = 'http://test.url'
        mock_create.return_value = mock_session

        mock_retrieve.return_value = MagicMock(
            payment_status='paid',
            payment_intent='test_intent'
        )

        # Шаг 1: Имитируем создание платежа
        response = self.client.get(reverse('users:create_payment', args=[self.content.id]))
        self.assertEqual(response.status_code, 200)

        # Шаг 2: Имитируем успешную оплату
        response = self.client.get(
            reverse('users:payment_success', args=[self.content.id]),
            {'session_id': 'test_session'}
        )

        # Проверяем создание подписки
        self.assertTrue(
            Subscription.objects.filter(
                user=self.user,
                content=self.content
            ).exists(),
            "Подписка не была создана после оплаты"
        )

        # Проверяем статус платежа
        payment = Payment.objects.get(session_id='test_session')
        self.assertEqual(payment.status, 'paid')


class ProfileViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(phone='79123456789', password='testpass')
        self.client.login(phone='79123456789', password='testpass')

    def test_profile_view(self):
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
