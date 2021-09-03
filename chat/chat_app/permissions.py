from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


class LoginRequired(LoginRequiredMixin):
    login_url = reverse_lazy('chat_app:login_view')
