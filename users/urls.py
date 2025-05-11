from django.urls import path

from . import views
from .views import CustomLoginView, UserRegistrationView, CreatePaymentView, \
    PaymentSuccessView, custom_logout, profile_view, \
    ProfileUpdateView, PhoneTokenObtainPairView, UserSubscriptionsList

from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .apps import UsersConfig

app_name = UsersConfig.name


urlpatterns = [
    path('payment/<int:pk>/', CreatePaymentView.as_view(), name='create_payment'),
    path('payment/payment_success/<int:pk>/', PaymentSuccessView.as_view(), name='payment_success'),
    path('api/token/', PhoneTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='edit_profile'),
    path('subscriptions/', UserSubscriptionsList.as_view(), name='subscriptions'),
    path('check_payment_status/<int:payment_id>/', views.check_payment_status, name='check_payment_status'),

]
