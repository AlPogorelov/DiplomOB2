from django.contrib.auth import get_user_model
from content.models import Category, Content, Media
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, RequestFactory
from django.urls import reverse
from content.forms import ContentForm, CategoryForm

User = get_user_model()


class CategoryModelTest(TestCase):
    def test_category_creation(self):
        category = Category.objects.create(name="Технологии")
        self.assertEqual(str(category), "Технологии")
        self.assertEqual(category._meta.verbose_name, "категория")
        self.assertEqual(category._meta.verbose_name_plural, "категории")


class ContentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(phone="+79123456789")
        self.category = Category.objects.create(name="Образование")

    def test_content_creation(self):
        content = Content.objects.create(
            owner=self.user,
            category=self.category,
            title="Новая статья",
            body_text="Текст статьи",
            sub_price=100.00
        )
        self.assertTrue(content.is_paid)
        self.assertEqual(content._meta.verbose_name, "Контент")
        self.assertEqual(content.viewers, 0)

    def test_viewers_increment(self):
        content = Content.objects.create(
            owner=self.user,
            category=self.category,
            title="Статья"
        )
        content.viewers += 1
        content.save()
        self.assertEqual(content.viewers, 1)


class MediaModelTest(TestCase):
    def setUp(self):
        # Создаем необходимые объекты
        self.user = get_user_model().objects.create(phone="+79123456789")
        self.category = Category.objects.create(name="Тестовая категория")
        self.content = Content.objects.create(
            owner=self.user,
            category=self.category,
            title="Тестовый контент"
        )

    def test_media_creation(self):
        media = Media.objects.create(
            content=self.content,  # Используем созданный content
            file=SimpleUploadedFile("test.txt", b"file content")
        )
        self.assertTrue(media.file.name.endswith('.txt'))
        self.assertIn('test', media.file.name)


class ContentViewsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(phone="+79123456789", password="testpass123")
        self.category = Category.objects.create(name="Наука")
        self.content = Content.objects.create(
            owner=self.user,
            category=self.category,
            title="Научная статья",
            sub_price=100.00
        )

    def test_home_view(self):
        response = self.client.get(reverse('content:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'content/home.html')

    def test_content_detail_access(self):
        # Тест доступа автора
        self.client.force_login(self.user)
        response = self.client.get(reverse('content:content_detail', args=[self.content.pk]))
        self.assertEqual(response.status_code, 200)

        # Тест перенаправления для неавторизованного пользователя
        self.client.logout()
        response = self.client.get(reverse('content:content_detail', args=[self.content.pk]))
        self.assertRedirects(response, f"/users/login/?next=/content/{self.content.pk}/")


class CategoryViewsTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="История")

    def test_category_list_view(self):
        response = self.client.get(reverse('content:categories_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "История")


class ContentCreateTest(TestCase):
    def test_content_creation_flow(self):
        user = User.objects.create_user(phone="+79123456789", password="testpass123")
        category = Category.objects.create(name="Технологии")

        self.client.force_login(user)
        response = self.client.post(reverse('content:content_create'), {
            'category': category.pk,
            'title': 'Новый контент',
            'body_text': 'Текст',
            'sub_price': 0
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Content.objects.count(), 1)


class ContentPermissionsTest(TestCase):
    def setUp(self):
        self.author = User.objects.create(phone="+79123456789")
        self.user = User.objects.create(phone="+79000000000")
        self.category = Category.objects.create(name="Финансы")
        self.content = Content.objects.create(
            owner=self.author,
            category=self.category,
            title="Финансовая статья"
        )

    def test_content_update_permission(self):
        # Попытка изменения чужого контента
        self.client.force_login(self.user)
        response = self.client.get(reverse('content:content_update', args=[self.content.pk]))
        self.assertEqual(response.status_code, 403)

    def test_owner_access(self):
        # Доступ автора
        self.client.force_login(self.author)
        response = self.client.get(reverse('content:content_update', args=[self.content.pk]))
        self.assertEqual(response.status_code, 200)


class CategoryPermissionsTest(TestCase):
    def test_category_delete_access(self):
        category = Category.objects.create(name="Временная категория")

        # Используем актуальное имя маршрута для входа
        login_url = reverse('users:login')  # Предполагая, что используется пространство имен 'users'

        response = self.client.get(
            reverse('content:category_delete', args=[category.pk])
        )

        expected_url = f"{login_url}?next={reverse('content:category_delete', args=[category.pk])}"
        self.assertRedirects(response, expected_url, fetch_redirect_response=False)


class ContentFilterTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(phone="+79123456789")
        self.category1 = Category.objects.create(name="Кино")
        self.category2 = Category.objects.create(name="Музыка")

        Content.objects.bulk_create([
            Content(owner=self.user, category=self.category1, title="Фильм 1", sub_price=0, published=True),
            Content(owner=self.user, category=self.category2, title="Альбом 1", sub_price=100, published=True),
        ])

    def test_category_filter(self):
        response = self.client.get(f"{reverse('content:home')}?category={self.category1.pk}")
        self.assertEqual(len(response.context['contents']), 1)
        self.assertEqual(response.context['contents'][0].category, self.category1)

    def test_free_content_filter(self):
        response = self.client.get(reverse('content:free_content'))
        self.assertEqual(len(response.context['contents']), 1)
        self.assertEqual(response.context['contents'][0].sub_price, 0)


class ContentFormTest(TestCase):
    def test_valid_content_form(self):
        category = Category.objects.create(name="Тест")
        user = User.objects.create(phone="+79000000000")

        form_data = {
            'category': category.pk,
            'title': 'Тестовая статья',
            'body_text': 'Содержание статьи',
            'sub_price': 0,
            'owner': user.pk
        }
        form = ContentForm(data=form_data)
        self.assertTrue(form.is_valid())


class CategoryFormTest(TestCase):
    def test_duplicate_category(self):
        Category.objects.create(name="Дубликат")
        form = CategoryForm(data={'name': 'Дубликат'})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
