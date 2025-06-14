# Generated by Django 5.2 on 2025-05-09 12:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Наименование')),
            ],
            options={
                'verbose_name': 'категория',
                'verbose_name_plural': 'категории',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, null=True, upload_to='media_contents/', verbose_name='Файл')),
            ],
            options={
                'verbose_name': 'Медиа файл',
                'verbose_name_plural': 'Медиа файлы',
            },
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Заголовок')),
                ('body_text', models.TextField(verbose_name='Основной текст контента')),
                ('published', models.BooleanField(default=False, verbose_name='Опубликовано')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('sub_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Цена подписки')),
                ('likes', models.IntegerField(default=0, verbose_name='Лайки')),
                ('viewers', models.IntegerField(default=0, verbose_name='Просмотры')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contents', to='content.category', verbose_name='Категория публикации')),
            ],
            options={
                'verbose_name': 'Контент',
                'verbose_name_plural': 'Контент',
                'ordering': ['-created_at', 'category', 'owner'],
            },
        ),
    ]
