from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from content.models import Content


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('The Phone field must be set')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone, password, **extra_fields)


class User(AbstractUser):

    email = models.EmailField(blank=True, null=True)
    username = None
    phone = models.CharField(
        max_length=15,
        verbose_name='Телефон',
        unique=True,
        blank=False,
        null=False,
        help_text="Введите номер телефона"
    )
    bio = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    content = models.ForeignKey('content.Content', on_delete=models.CASCADE,
                                related_name='content_payments', verbose_name='Контент')
    amount = models.PositiveIntegerField(verbose_name='Сумма платежа')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Ожидает оплаты'),
            ('paid', 'Оплачен'),
            ('canceled', 'Отменен')
        ],
        default='pending'
    )
    session_id = models.CharField(max_length=255, unique=True)
    stripe_payment_intent = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'Payment {self.id}'

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='user_subscriptions', verbose_name='Пользователь')
    content = models.ForeignKey(Content, on_delete=models.CASCADE,
                                related_name='content_subscriptions', verbose_name='Контент')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата подписки')
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, verbose_name='Платеж')
    is_active = models.BooleanField(default=False, verbose_name='Активна')

    class Meta:
        unique_together = ('user', 'content')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
