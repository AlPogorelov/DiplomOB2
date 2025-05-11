from rest_framework_simplejwt.views import TokenObtainPairView
import stripe
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from config import settings
from content.models import Content
from django.views.generic import CreateView, TemplateView, DetailView, UpdateView, View, ListView
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from .models import User, Subscription, Payment
from .forms import PhoneUserCreationForm, PhoneAuthenticationForm, UserUpdateForm, ProfileForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import PhoneTokenObtainPairSerializer

stripe.api_key = settings.STRIPE_API_KEY


class UserRegistrationView(CreateView):
    model = User
    form_class = PhoneUserCreationForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('content:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


def custom_logout(request):
    logout(request)
    return redirect('/content/home/')


class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    authentication_form = PhoneAuthenticationForm


class UserProfileView(LoginRequiredMixin, TemplateView):

    form_class = UserUpdateForm
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['subscriptions'] = Subscription.objects.filter(user=user)
        context['payments'] = Payment.objects.filter(user=user)

        return context


@login_required
def profile_view(request):
    return render(request, 'users/profile.html')


class AccessMixin:
    def dispatch(self, request, *args, **kwargs):
        content = self.get_object()
        if not content.is_paid or self.has_access(request.user, content):
            return super().dispatch(request, *args, **kwargs)
        return redirect('content-payment', pk=content.pk)

    def has_access(self, user, content):
        return user == content.owner or Subscription.objects.filter(
            user=user,
            content=content,
            is_active=True
        ).exists()


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


class PhoneTokenObtainPairView(TokenObtainPairView):
    serializer_class = PhoneTokenObtainPairSerializer


class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": f"Hello {request.user.phone}!",
            "user_id": request.user.id
        })


class CreatePaymentView(LoginRequiredMixin, DetailView):
    model = Content
    template_name = 'payments/create_payment.html'

    def get(self, request, *args, **kwargs):
        content = self.get_object()

        if Subscription.objects.filter(user=request.user, content=content).exists():
            return redirect(content.get_absolute_url())

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'rub',
                        'product_data': {'name': content.title},
                        'unit_amount': int(content.sub_price * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri(
                    reverse('users:payment_success', kwargs={'pk': content.pk})
                ),
                cancel_url=request.build_absolute_uri(
                    reverse('content:content_detail', kwargs={'pk': content.pk})
                ),
            )

            payment = Payment.objects.create(
                user=request.user,
                content=content,
                amount=content.sub_price,
                session_id=session.id,
                status='pending'
            )

            # Рендерим страницу с проверкой статуса
            return render(request, 'payments/payment_check.html', {
                'payment_id': payment.id,
                'session_id': session.id,
                'success_url': request.build_absolute_uri(
                    reverse('users:payment_success', kwargs={'pk': content.pk})
                ),
                'object': content,
            })

        except stripe.error.StripeError:
            messages.error(request, 'Ошибка при создании платежа')
            return redirect(content)


class UserSubscriptionsList(LoginRequiredMixin, ListView):
    model = Subscription
    template_name = 'subscription/subscription_list.html'
    context_object_name = 'subscriptions'

    def get_queryset(self):
        # получаем только активные подписки текущего пользователя
        return Subscription.objects.filter(user=self.request.user, is_active=True).select_related('content')


class PaymentSuccessView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        content = get_object_or_404(Content, pk=self.kwargs['pk'])
        session_id = request.GET.get("session_id")

        if not session_id:
            messages.error(request, "Не удалось подтвердить платеж")
            return redirect("content:home")

        try:
            # 1. Получаем платеж текущего пользователя
            payment = Payment.objects.get(
                session_id=session_id,
                user=request.user,
                content=content,
                status="pending"  # Обрабатываем только ожидающие платежи
            )

            # 2. Проверяем статус в Stripe
            session = stripe.checkout.Session.retrieve(session_id)

            if session.payment_status == "paid":
                # 3. Обновляем статус платежа
                payment.status = "paid"
                payment.stripe_payment_intent = session.payment_intent
                payment.save()

                # 4. Создаем подписку (если не существует)
                Subscription.objects.get_or_create(
                    user=request.user,
                    content=content,
                    defaults={'payment': payment}
                )

                messages.success(request, "Доступ к контенту успешно открыт!")
                return redirect(content.get_absolute_url())

            else:
                # Платеж не прошел
                payment.status = "canceled"
                payment.save()
                messages.warning(request, "Платеж не был завершен")
                return redirect("users:create_payment", pk=content.pk)

        except Payment.DoesNotExist:
            messages.error(request, "Платеж не найден")
            return redirect("content:home")

        except stripe.error.StripeError:
            # Логируем ошибку
            messages.error(request, "Ошибка при проверке платежа")
            return redirect("content:home")

        except Exception:
            # Общая ошибка
            messages.error(request, "Ошибка обработки платежа")
            return redirect("content:home")


def check_payment_status(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
        return JsonResponse({'status': payment.status})
    except Payment.DoesNotExist:
        return JsonResponse({'status': 'not_found'}, status=404)
