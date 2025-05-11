from django.db import models
from django.conf import settings
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=150, verbose_name='Наименование', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'
        ordering = ['name']


class Content(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='contents',
        verbose_name='Автор публикации'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='contents',
        verbose_name='Категория публикации'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок'
    )
    body_text = models.TextField(
        verbose_name='Основной текст контента'
    )
    published = models.BooleanField(
        default=False,
        verbose_name='Опубликовано'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    sub_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name='Цена подписки'
    )
    likes = models.IntegerField(
        default=0,
        verbose_name='Лайки'
    )
    viewers = models.IntegerField(
        default=0,
        verbose_name='Просмотры'
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('content:content_detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'Контент'
        verbose_name_plural = 'Контент'
        ordering = ['-created_at', 'category', 'owner']

    @property
    def is_paid(self):
        """Проверяет, является ли контент платным"""
        return self.sub_price > 0

class Media(models.Model):
    content = models.ForeignKey(
        Content,
        on_delete=models.CASCADE,
        related_name='media_files'
    )
    file = models.FileField(upload_to='media_contents/', blank=True, null=True, verbose_name='Файл')

    class Meta:
        verbose_name = 'Медиа файл'
        verbose_name_plural = 'Медиа файлы'
