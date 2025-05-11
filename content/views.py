from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy

from users.models import Subscription
from .forms import ContentForm, CategoryForm
from .models import Content, Category, Media
from django.db.models import Count
from django.core.exceptions import PermissionDenied


class HomeView(View):
    template_name = 'content/home.html'

    def get(self, request, *args, **kwargs):
        selected_category = request.GET.get('category')

        # Базовый запрос
        contents = Content.objects.all().prefetch_related('media_files').select_related('category')
        categories = Category.objects.all()

        # Фильтрация по категории
        if selected_category:
            contents = contents.filter(category_id=selected_category)

        context = {
            'contents': contents,
            'categories': categories,
            'selected_category': int(selected_category) if selected_category else None
        }
        return render(request, self.template_name, context)


class CategoryContentList(ListView):
    model = Content
    template_name = 'content/cat_category.html'
    context_object_name = 'contents'
    paginate_by = 10

    def get_queryset(self):
        category_id = self.kwargs['category_pk']
        return Content.objects.filter(category_id=category_id, published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs['category_pk']
        context['category'] = get_object_or_404(Category, id=category_id)
        return context


class ContentListView(ListView):
    model = Content
    template_name = 'content/content_list.html'
    context_object_name = 'contents'
    paginate_by = 10

    def get_queryset(self):
        return Content.objects.filter(published=True, sub_price=0)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class ContentDetailView(LoginRequiredMixin, DetailView):
    model = Content
    template_name = 'content/content_detail.html'
    context_object_name = 'content'
    pk_url_kwarg = 'pk'
    login_url = 'users:login'

    def dispatch(self, request, *args, **kwargs):
        # Сохраняем URL для перенаправления после входа
        request.session['next'] = request.get_full_path()
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Проверка доступа
        if not self.has_access():
            return self.handle_no_access()

        # Обновление счетчика просмотров
        self.object.viewers += 1
        self.object.save()

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def has_access(self):
        user = self.request.user
        content = self.object

        # Бесплатный контент — доступ всем, даже незарегистрированным
        if not content.is_paid:
            return True

        # Для платного контента: автор или активный подписчик
        if user.is_authenticated:
            if user == content.owner:
                return True
            elif Subscription.objects.filter(
                user=user,
                content=content,
                is_active=True
            ).exists():
                return True
        # Если пользователь не авторизован или не прошел проверку — доступ запрещен
        return False

    def handle_no_access(self):
        content = self.object
        user = self.request.user

        # Для платного контента — перенаправляем на оплату или логин
        if content.is_paid:
            if user.is_authenticated:
                return redirect('users:create_payment', pk=content.pk)
            else:
                return redirect('users:login')
        # Для бесплатного контента — показываем главную или другую страницу
        return redirect('content:home')


class ContentCreateView(LoginRequiredMixin, CreateView):
    model = Content
    form_class = ContentForm
    template_name = 'content/content_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)

        # Обработка медиафайлов
        files = self.request.FILES.getlist('media_files')
        for file in files:
            Media.objects.create(
                content=self.object,
                file=file
            )

        return response

    def get_success_url(self):
        return reverse_lazy('content:content_detail', kwargs={'pk': self.object.pk})


class ContentUpdateView(LoginRequiredMixin, UpdateView):
    model = Content
    form_class = ContentForm
    template_name = 'content/content_form.html'
    success_url = 'content:my_content'

    def form_valid(self, form):
        response = super().form_valid(form)

        # Обработка новых медиафайлов
        files = self.request.FILES.getlist('media_files')
        for file in files:
            Media.objects.create(
                content=self.object,
                file=file
            )

        return response

    def get_success_url(self):
        return reverse_lazy('content:content_detail', kwargs={'pk': self.object.pk})

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class ContentDeleteView(LoginRequiredMixin, DeleteView):
    model = Content
    template_name = 'content/confirm_delete.html'
    success_url = 'content:content_list'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != request.user:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class MyContentList(LoginRequiredMixin, ListView):
    model = Content
    template_name = 'content/my_content_list.html'
    context_object_name = 'contents'
    paginate_by = 10

    def get_queryset(self):
        return Content.objects.filter(
            owner=self.request.user
        ).order_by('-created_at')


class FreeContentList(ListView):
    model = Content
    template_name = 'content/my_content_list.html'
    context_object_name = 'contents'
    paginate_by = 10

    def get_queryset(self):
        return Content.objects.filter(
            published=True,
            sub_price=0
        ).order_by('-created_at')


class CategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Category
    template_name = 'content/category_form.html'
    form_class = CategoryForm
    success_url = reverse_lazy('content:categories_list')
    permission_required = 'content.add_category'


class CategoryListView(ListView):
    model = Category
    template_name = 'content/categories_list.html'
    context_object_name = 'categories'
    paginate_by = 10

    def get_queryset(self):
        return Category.objects.annotate(
            content_count=Count('contents', distinct=True)
        ).order_by('name')


class CategoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Category
    template_name = 'content/category_form.html'
    form_class = CategoryForm
    success_url = reverse_lazy('content/categories_list.html')
    pk_url_kwarg = 'category_pk'
    permission_required = 'content.change_category'


class CategoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Category
    template_name = 'content/category_delete.html'
    success_url = reverse_lazy('content:categories_list')
    pk_url_kwarg = 'category_pk'
    permission_required = 'content.delete_category'


class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = 'content/category_detail.html'
    context_object_name = 'category'
    pk_url_kwarg = 'category_pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contents'] = Content.objects.filter(category=self.object)
        return context
