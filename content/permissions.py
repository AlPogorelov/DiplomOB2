from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.shortcuts import redirect


class AuthRequiredMixin(LoginRequiredMixin):
    """Кастомный миксин с поддержкой next параметра"""
    def handle_no_permission(self):
        login_url = reverse('login')
        redirect_url = f"{login_url}?next={self.request.path}"
        return redirect(redirect_url)
